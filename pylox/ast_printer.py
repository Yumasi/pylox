from pylox.expr import Binary, Conditional, Expr, ExprVisitor, Grouping, Literal, Unary


class AstPrinter(ExprVisitor[str]):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visitConditionalExpr(self, expr: Conditional) -> str:
        return self._parenthesize("?", expr.condition, expr.left, expr.right)

    def visitBinaryExpr(self, expr: Binary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: Grouping) -> str:
        return self._parenthesize("group", expr.expression)

    def visitLiteralExpr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary) -> str:
        return self._parenthesize(expr.operator.lexeme, expr.right)

    def _parenthesize(self, name: str, *exprs: Expr) -> str:
        result = f"({name}"
        for expr in exprs:
            result += f" {expr.accept(self)}"
        result += ")"

        return result


class RPNAstPrinter(ExprVisitor[str]):
    def print(self, expr: Expr) -> str:
        return expr.accept(self)

    def visitConditionalExpr(self, expr: Conditional) -> str:
        return self._rpn("?", expr.condition, expr.left, expr.right)

    def visitBinaryExpr(self, expr: Binary) -> str:
        return self._rpn(expr.operator.lexeme, expr.left, expr.right)

    def visitGroupingExpr(self, expr: Grouping) -> str:
        return self._rpn("", expr.expression)

    def visitLiteralExpr(self, expr: Literal) -> str:
        if expr.value is None:
            return "nil"
        return str(expr.value)

    def visitUnaryExpr(self, expr: Unary) -> str:
        return self._rpn(expr.operator.lexeme, expr.right)

    def _rpn(self, name: str, *exprs: Expr) -> str:
        result = ""
        for expr in exprs:
            result += f"{expr.accept(self)} "
        result += name

        return result
