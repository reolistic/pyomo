__all__ = ('value_logical', 'LogicalValue', 'TrueConstant',
           'FalseConstant', 'native_logical_values')

import sys
import logging
from six import iteritems

from pyomo.core.expr.expr_errors import TemplateExpressionError
from pyomo.core.expr.numvalue import native_types, native_logical_types
from pyomo.core.expr.expr_common import _and, _or, _equiv, _inv, _xor, _impl

logger = logging.getLogger('pyomo.core')
native_logical_values = {True, False, 1, 0}

def _generate_logical_proposition(etype, _self, _other):
    raise RuntimeError("Incomplete import of Pyomo expression system")  #pragma: no cover


def value(obj, exception=True):
    #0-0 Thinkng about a way to make it work
    """

    Returns: A numeric value or None.
    """
   
    if obj.__class__ in native_logical_types:
        return bool(obj)
    if obj.__class__ is LogicalConstant:
        #   
        # do not expect LogicalConstant with value None.
        #
        #if exception and obj.value is None:
        #    raise ValueError(
        #        "No value for uninitialized LogicalConstant object %s"
        #        % (obj.name,))
        return obj.value
    # Test if we have a duck types for Pyomo expressions
    #
    try:
        obj.is_expression_type()
    except AttributeError:
        #
        # If not, then try to coerce this into a logical constant.  If that
        # works, then return the object
        #
        try:
            return obj
        except:
            raise TypeError(
                "Cannot evaluate object with unknown type: %s" %
                (type(obj).__name__,))
    #
    # Evaluate the expression object
    #
    if exception:
        #
        # Here, we try to catch the exception
        #
        try:
            tmp = obj(exception=True)
            if tmp is None:
                raise ValueError(
                    "No value for uninitialized LogicalcValue object %s"
                    % (obj.name,))
            return tmp
        except TemplateExpressionError:
            # Template expressions work by catching this error type. So
            # we should defer this error handling and not log an error
            # message.
            raise
        except:
            logger.error(
                "evaluating object as logical value: %s\n    (object: %s)\n%s"
                % (obj, type(obj), sys.exc_info()[1]))
            raise
    else:
        #
        # Here, we do not try to catch the exception
        #
        return obj(exception=False)
      

value_logical = value  
#assigning an alias to distinguish it from the numeric version

# def is_fixed(obj):
#     """
#     A utility function that returns a boolean that indicates
#     whether the input object's value is fixed.
#     """
#     # JDS: NB: I am not sure why we allow str to be a constant, but
#     # since we have historically done so, we check for type membership
#     # in native_types and not in native_numeric_types.
#     #
#     if obj.__class__ in native_types:
#         return True
#     try:
#         return obj.is_fixed()
#     except AttributeError:
#         pass
#     raise TypeError(
#         "Cannot assess properties of object with unknown type: %s"
#         % (type(obj).__name__,))
#
# def is_variable_type(obj):
#     """
#     A utility function that returns a boolean indicating
#     whether the input object is a variable.
#     """
#     if obj.__class__ in native_types:
#         # change native_types
#         return False
#     if (obj is 1 ) or (obj is 0):
#         # 0-0 change later
#         return False
#     try:
#         return obj.is_variable_type()
#     except AttributeError:
#         return False
#
# def is_potentially_variable(obj):
#     """
#     A utility function that returns a boolean indicating
#     whether the input object can reference variables.
#     """
#     if obj.__class__ in native_types:
#         return False
#     try:
#         return obj.is_potentially_variable()
#     except AttributeError:
#         return False

# _KnownConstants = {}
#tbc

def as_logical(obj):
    # raise error for anything other than {0,1,True,False}
    """
    A function that creates a LogicalConstant object that
    wraps Python logical values.

    Args:
        obj: The logical value that may be wrapped.

    Raises: TypeError if the object is in native_types and not in 
        native_logical_types

    Returns: A true or false LogicalConstant or the original object
    """
    #if obj.__class__ in native_logical_types or obj is 1 or obj is 0:
    if obj in native_logical_values:
        return LogicalConstant(obj)
    #
    # Ignore objects that are duck types to work with Pyomo expressions
    #
    try:
        obj.is_expression_type()
        return obj
    except AttributeError:
        pass
    #
    # Generate errors
    #
    if obj.__class__ in native_types:
        raise TypeError("Cannot treat the value '%s' as a logical constant" % str(obj))
    raise TypeError(
        "Cannot treat the value '%s' as a logical constant because it has unknown "
        "type '%s'" % (str(obj), type(obj).__name__))


class LogicalValue(object):
    #an abstract class 
    #
    #__slots__ = ('value',)
    __slots__ = ()
    __hash__ = None

    def __getstate__(self):
        _base = super(LogicalValue, self)
        if hasattr(_base, '__getstate__'):
            return _base.__getstate__()
        else:
            return {}

    def __setstate__(self, state):
        """
        Restore a pickled state into this instance
        Our model for setstate is for derived classes to modify
        the state dictionary as control passes up the inheritance
        hierarchy (using super() calls).  All assignment of state ->
        object attributes is handled at the last class before 'object',
        which may -- or may not (thanks to MRO) -- be here.
        """
        _base = super(LogicalValue, self)
        if hasattr(_base, '__setstate__'):
            return _base.__setstate__(state)
        else:
            for key, val in iteritems(state):
                # Note: per the Python data model docs, we explicitly
                # set the attribute using object.__setattr__() instead
                # of setting self.__dict__[key] = val.
                object.__setattr__(self, key, val)

    def getname(self, fully_qualified=False, name_buffer=None):
        """
        If this is a component, return the component's name on the owning
        block; otherwise return the value converted to a string
        """
        _base = super(LogicalValue, self)
        if hasattr(_base, 'getname'):
            return _base.getname(fully_qualified, name_buffer)
        else:
            return str(type(self))

    @property
    def name(self):
        return self.getname(fully_qualified=True)

    @property
    def local_name(self):
        return self.getname(fully_qualified=False)

    def cname(self, *args, **kwds):
        logger.warning(
            "DEPRECATED: The cname() method has been renamed to getname()." )
        return self.getname(*args, **kwds)

    def is_constant(self):
        """Return True if this Logical value is a constant value"""
        return False

    def is_fixed(self):
        """Return True if this is a non-constant value that has been fixed"""
        return False

    def is_parameter_type(self):
        """Return False unless this class is a parameter object"""
        return False

    def is_variable_type(self):
        """Return False unless this class is a variable object"""
        return False

    def is_potentially_variable(self):
        """Return True if variables can appear in this expression"""
        return True

    def is_named_expression_type(self):
        """Return True if this Logical value is a named expression"""
        return False

    def is_expression_type(self):
        """Return True if this Logical value is an expression"""
        return False

    def is_component_type(self):
        """Return True if this class is a Pyomo component"""
        return False

    def is_relational(self):
        """
        Return True if this Logical value represents a relational expression.
        """
        # TODO this is meaningless
        return False

    def is_indexed(self):
        """Return True if this Logical value is an indexed object"""
        return False

    def __float__(self):
        raise TypeError(
            "Implicit conversion of Pyomo LogicalValue type "
            "'%s' to a float is disabled." % (self.name,))

    def __int__(self):
        raise TypeError(
            "Implicit conversion of Pyomo LogicalValue type "
            "'%s' to an integer is disabled." % (self.name,))

    def __lt__(self, other):
        return TypeError(
            "Numeric comparison with LogicalValue %s is not allowed." % self.name)

    def __gt__(self, other):
        return TypeError(
            "Numeric comparison with LogicalValue %s is not allowed." % self.name)

    def __le__(self, other):
        return TypeError(
            "Numeric comparison with LogicalValue %s is not allowed." % self.name)

    def __ge__(self, other):
        return TypeError(
            "Numeric comparison with LogicalValue %s is not allowed." % self.name)
    
    def __add__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __sub__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __mul__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __div__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __truediv__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __pow__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __radd__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __rsub__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __rmul__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __rdiv__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __rtruediv__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __rpow__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __iadd__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __isub__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __imul__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __idiv__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __itruediv__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __ipow__(self, other):
        return TypeError("Unable to perform arithmetic operations between logical values.")

    def __neg__(self):
        return TypeError("""Negation operator on logical values is not defined.""")

    def __pos__(self):
        return TypeError("""Positive operator on logical values is not defined.""")

    def __abs__(self):
        return TypeError("""Absolute value operator on logical values is not defined.""")

    def __bool__(self):
        """Evaluation as a boolean (using if, and, or keywords)"""
        return TypeError("Use value() for finding the value of a LogicalValue.")

    def __eq__(self, other):
        return _generate_logical_proposition(_equiv, self, other)

    def equivalent_to(self, other):
        return _generate_logical_proposition(_equiv, self, other)

    def __and__(self, other):
        return _generate_logical_proposition(_and, self, other)

    def __or__(self, other):
        return _generate_logical_proposition(_or, self, other)

    def __invert__(self):
        return _generate_logical_proposition(_inv, self, None)

    def __xor__(self, other):
        return _generate_logical_proposition(_xor, self, other)

    def xor(self, other):
        return _generate_logical_proposition(_xor, self, other)

    def implies(self, other):
        return _generate_logical_proposition(_impl, self, other)

    # 0-0
    def to_string(self, verbose=None, labeler=None, smap=None,
                  compute_values=False):
        """
        Return a string representation of the expression tree.

        Args:
            verbose (bool): If :const:`True`, then the the string 
                representation consists of nested functions.  Otherwise,
                the string representation is an algebraic equation.
                Defaults to :const:`False`.
            labeler: An object that generates string labels for 
                variables in the expression tree.  Defaults to :const:`None`.

        Returns:
            A string representation for the expression tree.
        """
        if compute_values:
            try:
                return str(self())
            except:
                pass
        if not self.is_constant():
            if smap:
                return smap.getSymbol(self, labeler)
            elif labeler is not None:
                return labeler(self)
        return self.__str__()


class LogicalConstant(LogicalValue):
    """An object that contains a constant Logical value.

    Constructor Arguments:
        value           The initial value.
    """

    __slots__ = ('value',)

    def __init__(self, value):
        if value not in native_logical_values:
            raise TypeError('Not a valid LogicalValue. Unable to create a logical constant')
        self.value = value

    def __getstate__(self):
        state = super(LogicalConstant, self).__getstate__()
        for i in LogicalConstant.__slots__:
            state[i] = getattr(self, i)
        return state

    def is_constant(self):
        return True

    def is_fixed(self):
        return True

    def is_potentially_variable(self):
        return False

    def __str__(self):
        return str(self.value)

    def __nonzero__(self):
        raise ValueError(
            "Boolean constant cannot be compared to zero: '%s'"
            % (self.name,))

    def __bool__(self):
        return self.value

    def __call__(self, exception=True):
        """Return the constant value"""
        return self.value

    def pprint(self, ostream=None, verbose=False):
        if ostream is None:         #pragma:nocover
            ostream = sys.stdout
        ostream.write(str(self))


# We use as_logical() so that the constant is also in the cache
TrueConstant = as_logical(True)
FalseConstant = as_logical(False)