import time
from typing import Any, List

import pylox.lox_return as lox_return
from pylox.environment import Environment
from pylox.error import LoxError, LoxRuntimeError
from pylox.expr import (
    Assign,
    Binary,
    Call,
    Conditional,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Logical,
    Unary,
    Variable,
)
from pylox.stmt import (
    Block,
    Break,
    Expression,
    Function,
    If,
    Print,
    Return,
    Stmt,
    StmtVisitor,
    Var,
    While,
)
from pylox.token import Token
from pylox.token_type import TokenType


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    def __init__(self) -> None:
        from pylox.callable import LoxCallable

        class Clock(LoxCallable):
            def arity(self) -> int:
                return 0

            def call(self, interpreter: "Interpreter", arguments: List[Any]) -> Any:
                return time.time()

            def __str__(self) -> str:
                return "<native fn>"

        self.globals = Environment()
        self.environment = self.globals

        self.globals.define("clock", Clock())

    def interpret(self, statements: List[Stmt]) -> None:
        try:
            for statement in statements:
                self._execute(statement)
        except LoxRuntimeError as e:
            LoxError.runtimeError(e)

    def visitBinaryExpr(self, expr: Binary) -> Any:
        left = self._evaluate(expr.left)  # type: ignore
        right = self._evaluate(expr.right)  # type: ignore

        match expr.operator.type:
            case TokenType.BANG_EQUAL:
                return not left == right
            case TokenType.EQUAL_EQUAL:
                return left == right
            case TokenType.GREATER:
                self._checkNumberOperands(expr.operator, left, right)
                return left > right
            case TokenType.GREATER_EQUAL:
                self._checkNumberOperands(expr.operator, left, right)
                return left >= right
            case TokenType.LESS:
                self._checkNumberOperands(expr.operator, left, right)
                return left < right
            case TokenType.LESS_EQUAL:
                self._checkNumberOperands(expr.operator, left, right)
                return left <= right
            case TokenType.MINUS:
                self._checkNumberOperands(expr.operator, left, right)
                return left - right
            case TokenType.PLUS:
                if isinstance(left, float) and isinstance(right, float):
                    return left + right
                if isinstance(left, str) and isinstance(right, str):
                    return left + right
                if isinstance(left, str) or isinstance(right, str):
                    return self._stringify(left) + self._stringify(right)

                raise LoxRuntimeError(
                    expr.operator, "Operands must be two numbers or two strings."
                )
            case TokenType.SLASH:
                self._checkNumberOperands(expr.operator, left, right)

                if right == 0:
                    raise LoxRuntimeError(expr.operator, "division by zero")

                return left / right
            case TokenType.STAR:
                self._checkNumberOperands(expr.operator, left, right)
                return left * right

        # Unreachable
        return None

    def visitCallExpr(self, expr: Call) -> Any:
        from pylox.callable import LoxCallable

        callee = self._evaluate(expr.callee)
        arguments = [self._evaluate(argument) for argument in expr.arguments]

        if not isinstance(callee, LoxCallable):
            raise LoxRuntimeError(expr.paren, "Can only call functions and classes.")

        if len(arguments) != callee.arity():
            raise LoxRuntimeError(
                expr.paren,
                f"Expected {callee.arity()} arguments but got {len(arguments)}.",
            )

        return callee.call(self, arguments)

    def visitConditionalExpr(self, expr: Conditional) -> Any:
        return (
            self._evaluate(expr.left)
            if self._evaluate(expr.condition)
            else self._evaluate(expr.right)
        )  # type: ignore

    def visitGroupingExpr(self, expr: Grouping) -> Any:
        return self._evaluate(expr.expression)  # type: ignore

    def visitLiteralExpr(self, expr: Literal) -> Any:
        return expr.value

    def visitLogicalExpr(self, expr: Logical) -> Any:
        left = self._evaluate(expr.left)

        if expr.operator.type == TokenType.OR:
            if self._isTruthy(left):
                return left
        else:
            if not self._isTruthy(left):
                return left

        return self._evaluate(expr.right)

    def visitUnaryExpr(self, expr: Unary) -> Any:
        right = self._evaluate(expr.right)  # type: ignore

        match expr.operator.type:
            case TokenType.BANG:
                return not self._isTruthy(right)
            case TokenType.MINUS:
                self._checkNumberOperand(expr.operator, right)
                return -right

        # Unreachable
        return None

    def visitVariableExpr(self, expr: Variable) -> Any:
        return self.environment.get(expr.name)

    def visitBreakStmt(self, stmt: Break) -> None:
        raise Break()

    def visitExpressionStmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def visitFunctionStmt(self, stmt: Function) -> None:
        from pylox.function import LoxFunction

        function = LoxFunction(stmt, self.environment)
        self.environment.define(stmt.name.lexeme, function)

    def visitIfStmt(self, stmt: If) -> None:
        if self._isTruthy(self._evaluate(stmt.condition)):
            self._execute(stmt.thenBranch)
        elif stmt.elseBranch:
            self._execute(stmt.elseBranch)

    def visitPrintStmt(self, stmt: Print) -> None:
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visitReturnStmt(self, stmt: Return) -> None:
        value: Any = None
        if stmt.value is not None:
            value = self._evaluate(stmt.value)

        raise lox_return.Return(value)

    def visitVarStmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer:
            value = self._evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

    def visitWhileStmt(self, stmt: While) -> None:
        try:
            while self._isTruthy(self._evaluate(stmt.condition)):
                self._execute(stmt.body)
        except Break:
            pass

    def visitBlockStmt(self, stmt: Block) -> None:
        self._executeBlock(stmt.statements, Environment(self.environment))

    def visitAssignExpr(self, expr: Assign) -> Any:
        value = self._evaluate(expr.value)
        self.environment.assign(expr.name, value)

        return value

    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def _execute(self, stmt: Stmt) -> None:
        stmt.accept(self)

    def _executeBlock(self, statements: List[Stmt], environment: Environment):
        previous = self.environment

        try:
            self.environment = environment

            for statement in statements:
                self._execute(statement)

        finally:
            self.environment = previous

    def _isTruthy(self, object: Any) -> bool:
        if object is None:
            return False

        if isinstance(object, bool):
            return object

        return True

    def _checkNumberOperand(self, operator: Token, operand: Any) -> None:
        if isinstance(operand, float):
            return

        raise LoxRuntimeError(operator, "Operand must be a number.")

    def _checkNumberOperands(self, operator: Token, left: Any, right: Any) -> None:
        if isinstance(left, float) and isinstance(right, float):
            return

        raise LoxRuntimeError(operator, "Operands must be numbers")

    def _stringify(self, object: Any) -> str:
        if object is None:
            return "nil"

        if isinstance(object, float):
            text = str(object)
            if text.endswith(".0"):
                text = text[0 : len(text) - 2]

            return text

        if isinstance(object, bool):
            return "true" if object else "false"

        return str(object)


class Break(Exception):
    pass
