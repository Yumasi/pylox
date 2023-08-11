from typing import Any, List

from pylox.environment import Environment
from pylox.error import LoxError, LoxRuntimeError
from pylox.expr import (
    Assign,
    Binary,
    Conditional,
    Expr,
    ExprVisitor,
    Grouping,
    Literal,
    Unary,
    Variable,
)
from pylox.stmt import Block, Expression, Print, Stmt, StmtVisitor, Var
from pylox.token import Token
from pylox.token_type import TokenType


class Interpreter(ExprVisitor[Any], StmtVisitor[None]):
    def __init__(self) -> None:
        self.environment = Environment()

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

    def visitConditionalExpr(self, expr: Conditional) -> Any:
        return self._evaluate(expr.left) if self._evaluate(expr.condition) else self._evaluate(expr.right)  # type: ignore

    def visitGroupingExpr(self, expr: Grouping) -> Any:
        return self._evaluate(expr.expression)  # type: ignore

    def visitLiteralExpr(self, expr: Literal) -> Any:
        return expr.value

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

    def visitExpressionStmt(self, stmt: Expression) -> None:
        self._evaluate(stmt.expression)

    def visitPrintStmt(self, stmt: Print) -> None:
        value = self._evaluate(stmt.expression)
        print(self._stringify(value))

    def visitVarStmt(self, stmt: Var) -> None:
        value = None
        if stmt.initializer:
            value = self._evaluate(stmt.initializer)

        self.environment.define(stmt.name.lexeme, value)

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
