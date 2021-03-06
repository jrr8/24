from operator import add, sub, mul
from itertools import combinations
from math import ceil
from time import time
from random import randint


def div(a, b):
	if b == 0:
		return None
	return int(a / b) if a % b == 0 else None

def make_pairs(superset):
	subsets = []
	if len(superset) == 0:
		return {}
	for i in range(1, len(superset)):
		subsets.extend(combinations(superset, i))

	# subsets is now such that the i-th entry and the (n-i)-th entry are complements
	return {subsets[i]: subsets[len(subsets) - (i + 1)] for i in range(len(subsets) // 2)}

def frozen_multiset(iterable):
	items = {}
	for item in iterable:
		if item not in items:
			items[item] = 0
		items[item] += 1
	return frozenset(items.items())


class Expression:
	def evaluate(self):
		raise NotImplementedError

	def signature(self):
		raise NotImplementedError

	def __eq__(self, other):
		return self.__class__ == other.__class__ and self.signature() == other.signature()

	def __hash__(self):
		return hash(self.signature())


class SingleExpression(Expression):
	def __init__(self, term):
		try:
			self.term = int(term)
		except TypeError:
			raise TypeError("SingleExpression's term must be an int or int-like")

	def __str__(self):
		return str(self.term)

	def __repr__(self):
		return "SingleExpression({})".format(self.term)

	def evaluate(self):
		return self.term

	def signature(self):
		return self.term


class CompoundExpression(Expression):
	@staticmethod
	def try_single_expression(side):
		try:
			return SingleExpression(side)
		except TypeError:
			return side

	def evaluate(self):
		pass

	def signature(self):
		pass


class CommutativeExpression(CompoundExpression):
	def __init__(self, terms, operation):
		if operation not in [add, mul]:
			raise ValueError("Operation for CommutativeExpression must be commutative (i.e. addition or multiplication)")
		self.operation = operation

		terms = [CompoundExpression.try_single_expression(term) for term in terms]
		if not all([isinstance(term, Expression) for term in terms]):
			raise TypeError("Terms for CommutativeExpression must be SingleExpressions or CompoundExpressions")

		# Extract subterms from like expressions
		_terms = []
		for term in terms:
			if isinstance(term, CompoundExpression) and term.operation == operation:
				_terms.extend(term.terms)
			else:
				_terms.append(term)

		self.terms = tuple(_terms)

	def __str__(self):
		if self.operation is add:
			return ' + '.join([str(term) for term in self.terms])
		term_strings = []
		for term in self.terms:
			term_strings.append(str(term) if isinstance(term, SingleExpression) else '(' + str(term) + ')')
		return ' * '.join(term_strings)

	def __repr__(self):
		return 'CommutativeExpression({})'.format(self.__str__())

	def signature(self):
		return frozen_multiset([term.signature() for term in self.terms] + [self.operation])

	def evaluate(self):
		ct = 0 if self.operation is add else 1
		for term in self.terms:
			ct = self.operation(ct, term.evaluate())
		return ct


class NonCommutativeExpression(CompoundExpression):
	def __init__(self, lhs, rhs, operation):
		if operation not in [sub, div]:
			raise ValueError("Operation for NonCommutativeExpression must be list_subtraction or division")
		lhs = CompoundExpression.try_single_expression(lhs)
		rhs = CompoundExpression.try_single_expression(rhs)
		if not isinstance(lhs, Expression) or not isinstance(rhs, Expression):
			raise TypeError("Lhs and rhs for NonCommutativeExpression must be a subclass of Expression")
		self.lhs, self.rhs = lhs, rhs
		self.operation = operation

	def __str__(self):
		symbol = ' - ' if self.operation is sub else ' / '
		lhs = '(' + str(self.lhs) + ')' if isinstance(self.lhs, CompoundExpression) else str(self.lhs)
		rhs = '(' + str(self.rhs) + ')' if isinstance(self.rhs, CompoundExpression) else str(self.rhs)
		return lhs + symbol + rhs

	def __repr__(self):
		return 'NonCommutativeExpression({})'.format(self.__str__())

	def signature(self):
		return self.lhs, self.rhs, self.operation

	def evaluate(self):
		return self.operation(self.lhs.evaluate(), self.rhs.evaluate())



# def make_expressions(numbers):
# 	if len(numbers) == 1:
# 		return [SingleExpression(numbers[0])]
#
# 	if len(numbers) == 2:
# 		expressions = [CommutativeExpression(numbers, add),
# 		               CommutativeExpression(numbers, mul)
# 		               ]
# 		lhs, rhs = numbers
# 		if lhs > rhs:
# 			expressions.append(NonCommutativeExpression(lhs, rhs, sub))
# 		else:
# 			expressions.append(NonCommutativeExpression(rhs, lhs, sub))
# 		if div(lhs, rhs) is not None:
# 			expressions.append(NonCommutativeExpression(lhs, rhs, div))
# 		if div(rhs, lhs) is not None:
# 			expressions.append(NonCommutativeExpression(rhs, lhs, div))
# 		return expressions
#
# 	expressions = []
# 	pairs = make_pairs(numbers)
# 	while pairs:
# 		subset, complement = pairs.popitem()
# 		subset_expressions = make_expressions(subset)
# 		complement_expressions = make_expressions(complement)
# 		for first_expression in subset_expressions:
# 			for second_expression in complement_expressions:
# 				expressions.append(CommutativeExpression([first_expression, second_expression], add))
# 				expressions.append(CommutativeExpression([first_expression, second_expression], mul))
# 				lhs, rhs = first_expression.evaluate(), second_expression.evaluate()
# 				if lhs > rhs:
# 					expressions.append(NonCommutativeExpression(first_expression, second_expression, sub))
# 				else:
# 					expressions.append(NonCommutativeExpression(second_expression, first_expression, sub))
# 				if div(lhs, rhs) is not None:
# 					expressions.append(NonCommutativeExpression(first_expression, second_expression, div))
# 				if div(rhs, lhs) is not None:
# 					expressions.append(NonCommutativeExpression(second_expression, first_expression, div))
# 	expressions = set(expressions)
# 	return expressions
#
# def challenge_24():
# 	solutions = {}
#
# 	def lookup_or_calculate(numbers):
# 		signature = frozen_multiset(numbers)
# 		if signature not in solutions:
# 			solutions[signature] = [expression for expression in make_expressions(numbers) if expression.evaluate() == 24]
# 		return solutions[signature]
#
# 	return lookup_or_calculate

def challenge_24():
	expressions = {}

	def _combine_two(n, m):
		if not isinstance(n, Expression):
			n = SingleExpression(n)
		if not isinstance(m, Expression):
			m = SingleExpression(m)
		pair = [n, m]
		n, m = max(pair, key=lambda x: x.evaluate()), min(pair, key=lambda x: x.evaluate())
		_expressions = [CommutativeExpression(pair, add),
		                CommutativeExpression(pair, mul),
		                NonCommutativeExpression(n, m, sub)
		                ]
		if div(n.evaluate(), m.evaluate()) is not None:
			_expressions.append(NonCommutativeExpression(n, m, div))
		return _expressions

	def _make_expressions(numbers):
		if len(numbers) == 1:
			return [SingleExpression(numbers[0])]

		if len(numbers) == 2:
			return _combine_two(*numbers)

		_expressions = []
		pairs = make_pairs(numbers)
		while pairs:
			subset, complement = pairs.popitem()
			if subset not in expressions:
				expressions[subset] = _make_expressions(subset)
			if complement not in expressions:
				expressions[complement] = _make_expressions(complement)

			subset_expressions = expressions[subset]
			complement_expressions = expressions[complement]
			for first_expression in subset_expressions:
				for second_expression in complement_expressions:
					_expressions.extend(_combine_two(first_expression, second_expression))
		return set(_expressions)

	return lambda x: [i for i in _make_expressions(x) if i.evaluate() == 24]







s = challenge_24()
d = [2, 3, 4, 4]
t = time()
a = s(d)
print('found {} solutions in {} seconds (first version)'.format(len(a), time() - t))





