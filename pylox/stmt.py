from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional, Protocol, TypeVar

from pylox.expr import Expr
from pylox.token import Token

T = TypeVar("T", covariant=True)


class Stmt(ABC):
    @abstractmethod
    def accept(self, visitor: "StmtVisitor[T]") -> T:
        ...


@dataclass
class Block(Stmt):
    statements: List[Stmt]

    def accept(self, visitor: "StmtVisitor[T]") -> T:
        return visitor.visitBlockStmt(self)


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
    def visitBlockStmt(self, stmt: Block) -> T:
        ...

    def visitExpressionStmt(self, stmt: Expression) -> T:
        ...

    def visitPrintStmt(self, stmt: Print) -> T:
        ...

    def visitVarStmt(self, stmt: Var) -> T:
        ...
