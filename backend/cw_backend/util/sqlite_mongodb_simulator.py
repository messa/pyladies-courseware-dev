import bson
import sqlite3
from pymongo import ReturnDocument


class SQLiteMongoDBSimulator:

    def __init__(self, path):
        self._conn = sqlite3.connect(path)

    def __getitem__(self, key):
        return Collection(self._conn, key)


class Collection:

    def __init__(self, conn, name):
        self._conn = conn
        self._name = name

    def find(self, filter=None, projection=None):
        return FindObject(self._conn, self._name, filter, projection)

    async def insert_one(self, document):
        create_collection_table(self._conn, self._name)
        doc = fix_document_before_insert(document)
        q = f'INSERT INTO `{self._name}` (id, bson) VALUES (?, ?)'
        self._conn.execute(q, (encode_document_id(doc['_id']), bson.encode(doc)))
        self._conn.commit()

    async def find_one_and_update(self, filter, update, return_document=False):
        create_collection_table(self._conn, self._name)
        q = f'SELECT id, bson FROM `{self._name}`'
        for encoded_id, raw in self._conn.execute(q):
            doc = bson.decode(raw)
            if document_matches_filter(doc, filter):
                new_doc = update_document(doc, update)
                q = f'UPDATE `{self._name}` SET bson = ? WHERE id = ?'
                self._conn.execute(q, (bson.encode(new_doc), encoded_id))
                self._conn.commit()
                if return_document == ReturnDocument.BEFORE:
                    return doc
                elif return_document == ReturnDocument.AFTER:
                    return new_doc
                else:
                    raise Exception('Invalid value of return_document: {return_document!r}')
                return


class FindObject:

    def __init__(self, conn, collection_name, filter, projection):
        self._conn = conn
        self._collection_name = collection_name
        self._filter = filter
        self._projection = projection

    async def to_list(self, limit):
        create_collection_table(self._conn, self._collection_name)
        result = []
        q = f'SELECT id, bson FROM `{self._collection_name}`'
        for encoded_id, raw in self._conn.execute(q):
            doc = bson.decode(raw)
            if document_matches_filter(doc, self._filter):
                result.append(document_projection(doc, self._projection))
            if limit is not None and len(result) >= limit:
                break
        self._conn.commit()
        return result


def update_document(doc, update):
    assert isinstance(doc, dict)
    assert isinstance(update, dict)
    new_doc = dict(doc)
    for uk, uv in update.items():
        assert isinstance(uv, dict)
        if uk == '$inc':
            for uvk, uvv in uv.items():
                assert isinstance(uvv, (int, float))
                new_doc[uvk] = new_doc.get(uvk, 0) + uvv
        else:
            raise Exception(f'Unsupported update key: {uk!r}')
    if new_doc['_id'] != doc['_id']:
        raise Exception('Cannot change document id')
    return new_doc



def fix_document_before_insert(document):
    doc = dict(document)
    doc.setdefault('_id', bson.ObjectId())
    return doc


def encode_document_id(doc_id):
    return bson.encode({'_id': doc_id})


def create_collection_table(conn, name):
    conn.execute(f'''
        CREATE TABLE IF NOT EXISTS `{name}` (
            id BLOB,
            bson BLOB,
            PRIMARY KEY (id)
        )
    ''')


def document_matches_filter(doc, f):
    if not f:
        return True
    assert isinstance(f, dict)
    for fk, fv in f.items():
        dv = doc.get(fk, None)
        if isinstance(fv, dict):
            raise Exception(f'Unsupported filter field: {fv!r}')
        elif dv != fv:
            return False

    return True
    raise Exception(f'Unsupported filter: {f!r}')


def document_projection(doc, p):
    if not p:
        return doc
    raise Exception('Unsupported projection')



