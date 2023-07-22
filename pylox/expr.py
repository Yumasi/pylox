from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional, Protocol, TypeVar

from pylox.token import Token

T = TypeVar("T", covariant=True)


class Expr(ABC):
    @abstractmethod
    def accept(self, visitor: "ExprVisitor[T]") -> T:
        ...


@dataclass
class Conditional(Expr):
    condition: Optional[Expr]
    left: Optional[Expr]
    right: Optional[Expr]

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitConditionalExpr(self)


@dataclass
class Assign(Expr):
    name: Token
    value: Expr

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitAssignExpr(self)


@dataclass
class Binary(Expr):
    left: Optional[Expr]
    operator: Token
    right: Optional[Expr]

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitBinaryExpr(self)


@dataclass
class Grouping(Expr):
    expression: Optional[Expr]

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
    right: Optional[Expr]

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitUnaryExpr(self)


@dataclass
class Variable(Expr):
    name: Token

    def accept(self, visitor: "ExprVisitor[T]") -> T:
        return visitor.visitVariableExpr(self)


class ExprVisitor(Protocol[T]):
    def visitConditionalExpr(self, expr: Conditional) -> T:
        ...

    def visitAssignExpr(self, expr: Assign) -> T:
        ...

    def visitBinaryExpr(self, expr: Binary) -> T:
        ...

    def visitGroupingExpr(self, expr: Grouping) -> T:
        ...

    def visitLiteralExpr(self, expr: Literal) -> T:
        ...

    def visitUnaryExpr(self, expr: Unary) -> T:
        ...

    def visitVariableExpr(self, expr: Variable) -> T:
        ...
