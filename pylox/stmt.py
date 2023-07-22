from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, Protocol, TypeVar

from pylox.token import Token
from pylox.expr import Expr

T = TypeVar("T", covariant=True)


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: "StmtVisitor[T]") -> T:
        ...


@dataclass
class Expression(Stmt):
    expression: Expr

    def accept(self, visitor: "StmtVisitor[T]") -> T:
        return visitor.visitExpressionStmt(self)


@dataclass
class Print(Stmt):
    expression: Expr

    def accept(self, visitor: "StmtVisitor[T]") -> T:
        return visitor.visitPrintStmt(self)


@dataclass
class Var(Stmt):
    name: Token
    initializer: Optional[Expr]

    def accept(self, visitor: "StmtVisitor[T]") -> T:
        return visitor.visitVarStmt(self)


class StmtVisitor(Protocol[T]):
    def visitExpressionStmt(self, stmt: Expression) -> T:
        ...

    def visitPrintStmt(self, stmt: Print) -> T:
        ...

    def visitVarStmt(self, stmt: Var) -> T:
        ...
