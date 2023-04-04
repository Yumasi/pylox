from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Protocol, TypeVar

from pylox.token import Token

T = TypeVar("T", covariant=True)


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: "ExprVisitor[T]") -> T:
        ...


@dataclass
class Conditional(Expr):
    condition: Expr
    left: Expr
    right: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitConditionalExpr(self)


@dataclass
class Binary(Expr):
    left: Expr
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitBinaryExpr(self)


@dataclass
class Grouping(Expr):
    expression: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitGroupingExpr(self)


@dataclass
class Literal(Expr):
    value: Any

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitLiteralExpr(self)


@dataclass
class Unary(Expr):
    operator: Token
    right: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitUnaryExpr(self)


class ExprVisitor(Protocol[T]):
    def visitConditionalExpr(self, expr: Conditional) -> T:
        ...

    def visitBinaryExpr(self, expr: Binary) -> T:
        ...

    def visitGroupingExpr(self, expr: Grouping) -> T:
        ...

    def visitLiteralExpr(self, expr: Literal) -> T:
        ...

    def visitUnaryExpr(self, expr: Unary) -> T:
        ...
