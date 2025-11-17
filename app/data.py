from os import getenv

from certifi import where
from dotenv import load_dotenv
from BloomtechMonsterLab import Monster
from pandas import DataFrame
from pymongo import MongoClient

from dotenv import load_dotenv

load_dotenv()   # Load .env variables such as DB_URL


"""
Database interface for Bandersnatch project.

Provides:
- Database(): class that encapsulates connection and collection operations.
- seed(amount): create `amount` random monsters and insert into collection.
- reset(): delete all documents from collection.
- count(): return int number of documents.
- dataframe(): return pandas.DataFrame of all documents (with _id as string).
- html_table(): return HTML table (or None if no docs).
"""


# The database name can be configured via the DB_NAME env var; default to "Bandersnatch"
DATABASE_NAME = getenv("DB_NAME", "Bandersnatch")

class Database:
    '''MongoDB-backed interface for the Monster collection.
    
    Environment variables expected:
    - DB_URL: MongoDB connection string (mongodb+srv://Mylabsproject:< SdL40wP42o2PgZrP >@cluster0.og3r23m.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0)
    
    Uses lsCAFile from certifi for secure connections.
    '''
   
    
    def __init__(self, DB_Name: str = 'bandersnatch', collections: str = 'monsters'):    
        '''Create a Database helper bound to a collection name.
        
        Args:
            collection: the collection name to use withing the configured database.
        '''
        db_url = getenv('DB_URL')
        if not db_url:
            raise RuntimeError('DB_URL environment variable not set. Put it into a .env file.')
        
        # Connect securely with certifi
        self.client = MongoClient(db_url, tls=True, tlsCAFile=where())
        self.database = self.client[DB_Name]
        self.collection = self.database[collections]

    def seed(self, amount):
        '''Populate the configured collection with "amount" random monsters.
        
        Uses BloomtechMonsterLab.Monster to generate each document. This function will insert documents in batches using 
        insert_many for efficiency.
        
        Args:
            amount: number of monster documents to create (should be >= 0).
        
        Returns: 
            The number of documents actually inserted.
        '''
        if amount <= 0:
            return 0
            
        # Generate list of plain dicts (omit any objectId / non-serializable field)
        docs = []
        for _ in range(amount):
            monsters = Monster().to_dict() 
            docs.append(monsters)
        
        # Insert and return count inserted (acknoledgement-safe)
        result = self.collection.insert_many(docs)
        return len(result.inserted_ids)

    def reset(self) -> int:
        '''
        Delete all documents in the collection.
        Returns the count of documents deleted.
        '''
        result = self.collection.delete_many({})
        return result.deleted_count 

    def count(self) -> int:
        '''
        Return the number of documents in the collection.
        '''
        return int(self.collection.count_documents({}))
        
    def dataframe(self) -> DataFrame:
        '''Return a pandas.DaataFrame of all document in the collection.
        
        If the collection is emmpty, an empty DataFrame is returned (no exceptions)
        '''
        docs = list(self.collection.find({}, {'_id': 0}))
        if not docs:
            return DataFrame()
        
        df = DataFrame(docs)
        return df

    def html_table(self) -> str:
        '''Return an HTML table representation of the collection documents.
        
        Returns:
            HTLM string for the table (bootstrap-friendly classes added), or None None when 
            the collection has no documents.
        '''
        df = self.dataframe()
        if df.empty:
            return None
        
        #index = False to avoid eposing the DataFrame index column in HTML table 
        return df.to_html(classes='table table-striped', index=False, escape=False)
    
if __name__ == "__main__":
    #Quick local smoke test (only runs when executed directly). Do not print from library code 
    # Keep behavior minimal, so it is safe to import in the Flask App.
    
    db = Database()
    db.reset()
    db.seed(1000)
    print(f'Current count: {db.count()}')
    