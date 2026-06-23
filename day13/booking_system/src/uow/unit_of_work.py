class UnitOfWork:

    def commit(self):
        print("Commit")

    def rollback(self):
        print("Rollback")