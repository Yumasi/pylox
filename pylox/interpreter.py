from typing import Any
from pylox.error import LoxError, LoxRuntimeError

from pylox.expr import Binary, Conditional, Expr, ExprVisitor, Grouping, Literal, Unary
from pylox.token import Token
from pylox.token_type import TokenType


class Interpreter(ExprVisitor[Any]):
    def interpret(self, expr: Expr) -> None:
        try:
            value: Any = self._evaluate(expr)
            print(self._stringify(value))
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
                if type(left) is float and type(right) is float:
                    return left + right
                if type(left) is str and type(right) is str:
                    return left + right
                if type(left) is str or type(right) is str:
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
        return None  # TODO

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

    def _evaluate(self, expr: Expr) -> Any:
        return expr.accept(self)

    def _isTruthy(self, object: Any) -> bool:
        if object is None:
            return False

        if type(object) is bool:
            return object

        return True

    def _checkNumberOperand(self, operator: Token, operand: Any) -> None:
        if type(operand) is float:
            return

        raise LoxRuntimeError(operator, "Operand must be a number.")

    def _checkNumberOperands(self, operator: Token, left: Any, right: Any) -> None:
        if type(left) is float and type(right) is float:
            return

        raise LoxRuntimeError(operator, "Operands must be numbers")

    def _stringify(self, object: Any) -> str:
        if object is None:
            return "nil"

        if type(object) is float:
            text = str(object)
            if text.endswith(".0"):
                text = text[0:len(text) - 2]

            return text

        if type(object) is bool:
            return "true" if object else "false"

        return str(object)
