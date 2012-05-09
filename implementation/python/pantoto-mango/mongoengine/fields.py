from base import BaseField, ObjectIdField, ValidationError, get_document
from document import Document, EmbeddedDocument
from operator import itemgetter

import re
import pymongo
import bson
import datetime
import decimal
from mongoengine.connection import Connection


__all__ = ['StringField', 'TextField','PasswordField','IntField', 'FloatField', 'BooleanField',
           'DateTimeField', 'EmbeddedDocumentField', 'ListField', 'DictField',
           'ObjectIdField', 'ReferenceField', 'ValidationError',
           'DecimalField', 'URLField', 'GenericReferenceField',
           'BinaryField', 'SortedListField', 'EmailField','SlugField', 'GeoLocationField']

RECURSIVE_REFERENCE_CONSTANT = 'self'

def to_bool(value):
    if value == 'True' or value == 'true' or value == '1' or value == 1:
        return True
    else:
        return False

class StringField(BaseField):
    """A unicode string field.
    """

    def __init__(self, regex=None, max_length=None, min_length=None, **kwargs):
        self.regex = re.compile(regex) if regex else None
        self.max_length = max_length
        self.min_length = min_length
        super(StringField, self).__init__(**kwargs)

    def to_python(self, value):
        return unicode(value)

    def validate(self, value):
        assert isinstance(value, (str, unicode))

        if self.max_length is not None and len(value) > self.max_length:
            raise ValidationError('String value is too long')
        
        if self.min_length is not None and len(value) < self.min_length:
            raise ValidationError('String value is too short')

        if self.regex is not None and self.regex.match(value) is None:
            message = 'String value did not match validation regex'
            raise ValidationError(message)

    def lookup_member(self, member_name):
        return None

    def prepare_query_value(self, op, value):
        if not isinstance(op, basestring):
            return value

        if op.lstrip('i') in ('startswith', 'endswith', 'contains', 'exact'):
            flags = 0
            if op.startswith('i'):
                flags = re.IGNORECASE
                op = op.lstrip('i')

            regex = r'%s'
            if op == 'startswith':
                regex = r'^%s'
            elif op == 'endswith':
                regex = r'%s$'
            elif op == 'exact':
                regex = r'^%s$'
            value = re.compile(regex % value, flags)
        return value


class URLField(StringField):
    """A field that validates input as an URL.

    .. versionadded:: 0.3
    """

    URL_REGEX = re.compile(
        r'^https?://'
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'
        r'localhost|'
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'
        r'(?::\d+)?'
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )

    def __init__(self, verify_exists=False, **kwargs):
        self.verify_exists = verify_exists
        super(URLField, self).__init__(**kwargs)

    def validate(self, value):
        if not URLField.URL_REGEX.match(value):
            raise ValidationError('Invalid URL: %s' % value)

        if self.verify_exists:
            import urllib2
            try:
                request = urllib2.Request(value)
                response = urllib2.urlopen(request)
            except Exception, e:
                message = 'This URL appears to be a broken link: %s' % e
                raise ValidationError(message)

class EmailField(StringField):
    """A field that validates input as an E-Mail-Address.
    """

    EMAIL_REGEX = re.compile(
        r"(^[-!#$%&'*+/=?^_`{}|~0-9A-Z]+(\.[-!#$%&'*+/=?^_`{}|~0-9A-Z]+)*"  # dot-atom
        r'|^"([\001-\010\013\014\016-\037!#-\[\]-\177]|\\[\001-011\013\014\016-\177])*"' # quoted-string
        r')@(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?$', re.IGNORECASE # domain
    )
    
    def validate(self, value):
        if not EmailField.EMAIL_REGEX.match(value):
            raise ValidationError('Invalid Mail-address: %s' % value)

class TextField(StringField):
    """
        Text Field.
    """
   
    def validate(self, value):
        return

class PasswordField(StringField):
    """
        Password Field.
    """
   
    def validate(self, value):
        super(PasswordField,self).validate(value)

class SlugField(StringField):
    """
        A field that validates input as Slug Field.
    """
    SLUG_REGEX = re.compile(r'^[-\w]+$')

    def validate(self, value):
        if not SlugField.SLUG_REGEX.match(value):
            raise ValidationError('Invalid Slug Field: %s' % value)


class IntField(BaseField):
    """An integer field.
    """

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(IntField, self).__init__(**kwargs)

    def to_python(self, value):
        return int(value)

    def validate(self, value):
        try:
            value = int(value)
        except:
            raise ValidationError('%s could not be converted to int' % value)

        if self.min_value is not None and value < self.min_value:
            raise ValidationError('Integer value is too small')

        if self.max_value is not None and value > self.max_value:
            raise ValidationError('Integer value is too large')

class FloatField(BaseField):
    """An floating point number field.
    """

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(FloatField, self).__init__(**kwargs)

    def to_python(self, value):
        return float(value)

    def validate(self, value):
        if isinstance(value, int):
            value = float(value)
        assert isinstance(value, float)

        if self.min_value is not None and value < self.min_value:
            raise ValidationError('Float value is too small')

        if self.max_value is not None and value > self.max_value:
            raise ValidationError('Float value is too large')

class DecimalField(BaseField):
    """A fixed-point decimal number field.

    .. versionadded:: 0.3
    """

    def __init__(self, min_value=None, max_value=None, **kwargs):
        self.min_value, self.max_value = min_value, max_value
        super(DecimalField, self).__init__(**kwargs)

    def to_python(self, value):
        if not isinstance(value, basestring):
            value = unicode(value)
        return decimal.Decimal(value)
    
    def to_mongo(self, value):
        return unicode(value)

    def validate(self, value):
        if not isinstance(value, decimal.Decimal):
            if not isinstance(value, basestring):
                value = str(value)
            try:
                value = decimal.Decimal(value)
            except Exception, exc:
                raise ValidationError('Could not convert to decimal: %s' % exc)

        if self.min_value is not None and value < self.min_value:
            raise ValidationError('Decimal value is too small')

        if self.max_value is not None and value > self.max_value:
            raise ValidationError('Decimal value is too large')

class BooleanField(BaseField):
    """A boolean field type.

    .. versionadded:: 0.1.2
    """

    def to_python(self, value):
        return bool(value)

    def validate(self, value):
        assert isinstance(to_bool(value), bool)

class DateTimeField(BaseField):
    """A datetime field.
    """

    def validate(self, value):
        assert isinstance(value, datetime.datetime)

class EmbeddedDocumentField(BaseField):
    """An embedded document field. Only valid values are subclasses of
    :class:`~mongoengine.EmbeddedDocument`.
    """

    def __init__(self, document, **kwargs):
        if not issubclass(document, EmbeddedDocument):
            raise ValidationError('Invalid embedded document class provided '
                                  'to an EmbeddedDocumentField')
        self.document = document
        super(EmbeddedDocumentField, self).__init__(**kwargs)

    def to_python(self, value):
        if not isinstance(value, self.document):
            return self.document._from_son(value)
        return value

    def to_mongo(self, value):
        return self.document.to_mongo(value)

    def validate(self, value):
        """Make sure that the document instance is an instance of the
        EmbeddedDocument subclass provided when the document was defined.
        """
        # Using isinstance also works for subclasses of self.document
        if not isinstance(value, self.document):
            raise ValidationError('Invalid embedded document instance '
                                  'provided to an EmbeddedDocumentField')
        self.document.validate(value)

    def lookup_member(self, member_name):
        return self.document._fields.get(member_name)

    def prepare_query_value(self, op, value):
        return self.to_mongo(value)


class ListField(BaseField):
    """A list field that wraps a standard field, allowing multiple instances
    of the field to be used as a list in the database.
    """

    # ListFields cannot be indexed with _types - MongoDB doesn't support this
    _index_with_types = False

    def __init__(self, field, **kwargs):
        if not isinstance(field, BaseField):
            raise ValidationError('Argument to ListField constructor must be '
                                  'a valid field')
        self.field = field
        super(ListField, self).__init__(**kwargs)

    def __get__(self, instance, owner):
        """Descriptor to automatically dereference references.
        """
        if instance is None:
            # Document class being used rather than a document object
            return self

        if isinstance(self.field, ReferenceField):
            referenced_type = self.field.document_type
            # Get value from document instance if available 
            value_list = instance._data.get(self.name)
            if value_list:
                deref_list = []
                for value in value_list:
                    # Dereference DBRefs
                    if isinstance(value, (bson.dbref.DBRef)):
                        value = Connection()._get_db().dereference(value)
                        deref_list.append(referenced_type._from_son(value))
                    else:
                        deref_list.append(value)
                instance._data[self.name] = deref_list

        if isinstance(self.field, GenericReferenceField):
            value_list = instance._data.get(self.name)
            if value_list:
                deref_list = []
                for value in value_list:
                    # Dereference DBRefs
                    if isinstance(value, (dict, pymongo.son.SON)):
                        deref_list.append(self.field.dereference(value))
                    else:
                        deref_list.append(value)
                instance._data[self.name] = deref_list

        return super(ListField, self).__get__(instance, owner)

    def to_python(self, value):
        return [self.field.to_python(item) for item in value]

    def to_mongo(self, value):
        return [self.field.to_mongo(item) for item in value]

    def validate(self, value):
        """Make sure that a list of valid fields is being used.
        """
        if not isinstance(value, (list, tuple)):
            raise ValidationError('Only lists and tuples may be used in a '
                                  'list field')

        try:
            [self.field.validate(item) for item in value]
        except Exception, err:
            raise ValidationError('Invalid ListField item (%s)' % str(err))

    def prepare_query_value(self, op, value):
        if op in ('set', 'unset'):
            return [self.field.to_mongo(v) for v in value]
        return self.field.to_mongo(value)

    def lookup_member(self, member_name):
        return self.field.lookup_member(member_name)

class SortedListField(ListField):
    """A ListField that sorts the contents of its list before writing to
    the database in order to ensure that a sorted list is always
    retrieved.
    """

    _ordering = None

    def __init__(self, field, **kwargs):
        if 'ordering' in kwargs.keys():
            self._ordering = kwargs.pop('ordering')
        super(SortedListField, self).__init__(field, **kwargs)

    def to_mongo(self, value):
        if self._ordering is not None:
            return sorted([self.field.to_mongo(item) for item in value], key=itemgetter(self._ordering))
        return sorted([self.field.to_mongo(item) for item in value])

class DictField(BaseField):
    """A dictionary field that wraps a standard Python dictionary. This is
    similar to an embedded document, but the structure is not defined.

    .. versionadded:: 0.3
    """

    def __init__(self, basecls=None, *args, **kwargs):
        self.basecls = basecls or BaseField
        assert issubclass(self.basecls, BaseField)
        super(DictField, self).__init__(*args, **kwargs)

    def validate(self, value):
        """Make sure that a list of valid fields is being used.
        """
        if not isinstance(value, dict):
            raise ValidationError('Only dictionaries may be used in a '
                                  'DictField')

        if any(('.' in k or '$' in k) for k in value):
            raise ValidationError('Invalid dictionary key name - keys may not '
                                  'contain "." or "$" characters')

    def lookup_member(self, member_name):
        return self.basecls(db_field=member_name)

class GeoLocationField(DictField):
    """Supports geobased fields"""
    
    def validate(self, value):
        """Make sure that a geo-value is of type (x, y)
        """
        if not isinstance(value, tuple) and not isinstance(value, list):
            raise ValidationError('GeoLocationField can only hold tuples or lists of (x, y)')
        
        if len(value) <> 2:
            raise ValidationError('GeoLocationField must have exactly two elements (x, y)')
    
    def to_mongo(self, value):
        return {'x': value[0], 'y': value[1]}
    
    def to_python(self, value):
        return value.keys()

class ReferenceField(BaseField):
    """A reference to a document that will be automatically dereferenced on
    access (lazily).
    """

    def __init__(self, document_type, **kwargs):
        if not isinstance(document_type, basestring):
            if not issubclass(document_type, (Document, basestring)):
                raise ValidationError('Argument to ReferenceField constructor '
                                      'must be a document class or a string')
        self.document_type_obj = document_type
        self.document_obj = None
        super(ReferenceField, self).__init__(**kwargs)

    @property
    def document_type(self):
        if isinstance(self.document_type_obj, basestring):
            if self.document_type_obj == RECURSIVE_REFERENCE_CONSTANT:
                self.document_type_obj = self.owner_document
            else:
                self.document_type_obj = get_document(self.document_type_obj)
        return self.document_type_obj

    def __get__(self, instance, owner):
        """Descriptor to allow lazy dereferencing.
        """
        if instance is None:
            # Document class being used rather than a document object
            return self

        # Get value from document instance if available
        value = instance._data.get(self.name)
        # Dereference DBRefs
        if isinstance(value, (bson.dbref.DBRef)):
            value = Connection()._get_db().dereference(value)
            if value is not None:
                instance._data[self.name] = self.document_type._from_son(value)

        return super(ReferenceField, self).__get__(instance, owner)

    def to_mongo(self, document):
        id_field_name = self.document_type._meta['id_field']
        id_field = self.document_type._fields[id_field_name]

        if isinstance(document, Document):
            # We need the id from the saved object to create the DBRef
            id_ = document.id
            if id_ is None:
                raise ValidationError('You can only reference documents once '
                                      'they have been saved to the database')
        else:
            id_ = document

        id_ = id_field.to_mongo(id_)
        collection = self.document_type._meta['collection']
        return bson.dbref.DBRef(collection, id_)

    def prepare_query_value(self, op, value):
        return self.to_mongo(value)

    def validate(self, value):
        # Add by Prashanth to work with form.cleaned_data ( ids will be string )
        if type(value).__name__ == 'unicode' or type(value).__name__ == 'str':
            try:
                obj = self.document_type.objects.get(id=value)
                value = obj
            except self.document_type.DoesNotExit:
                pass
        assert isinstance(value, (self.document_type, bson.dbref.DBRef))

    def lookup_member(self, member_name):
        return self.document_type._fields.get(member_name)


class GenericReferenceField(BaseField):
    """A reference to *any* :class:`~mongoengine.document.Document` subclass
    that will be automatically dereferenced on access (lazily).

    .. versionadded:: 0.3
    """

    def __get__(self, instance, owner):
        if instance is None:
            return self

        value = instance._data.get(self.name)
        if isinstance(value, (dict, pymongo.son.SON)):
            instance._data[self.name] = self.dereference(value)

        return super(GenericReferenceField, self).__get__(instance, owner)

    def dereference(self, value):
        doc_cls = get_document(value['_cls'])
        reference = value['_ref']
        doc = Connection()._get_db().dereference(reference)
        if doc is not None:
            doc = doc_cls._from_son(doc)
        return doc

    def to_mongo(self, document):
        id_field_name = document.__class__._meta['id_field']
        id_field = document.__class__._fields[id_field_name]

        if isinstance(document, Document):
            # We need the id from the saved object to create the DBRef
            id_ = document.id
            if id_ is None:
                raise ValidationError('You can only reference documents once '
                                      'they have been saved to the database')
        else:
            id_ = document

        id_ = id_field.to_mongo(id_)
        collection = document._meta['collection']
        ref = bson.dbref.DBRef(collection, id_)
        return {'_cls': document.__class__.__name__, '_ref': ref}

    def prepare_query_value(self, op, value):
        return self.to_mongo(value)['_ref']

class BinaryField(BaseField):
    """A binary data field.
    """

    def __init__(self, max_bytes=None, **kwargs):
        self.max_bytes = max_bytes
        super(BinaryField, self).__init__(**kwargs)

    def to_mongo(self, value):
        return pymongo.binary.Binary(value)

    def to_python(self, value):
        # Returns str not unicode as this is binary data
        return str(value)

    def validate(self, value):
        assert isinstance(value, str)

        if self.max_bytes is not None and len(value) > self.max_bytes:
            raise ValidationError('Binary value is too long')
