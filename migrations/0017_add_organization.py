from redash.models import db, Organization, Group
from redash import settings
from playhouse.migrate import PostgresqlMigrator, migrate

if __name__ == '__main__':
    if len(settings.GOOGLE_APPS_DOMAIN) > 1:
        print "#" * 80
        print "re:dash currently doesn't support more than one Google Apps domains."
        print "If this is an issue for you, please report it on GitHub."
        print "Currently re:dash will support only your first defined Google Apps Domain:"
        print "#" * 80
        print settings.GOOGLE_APPS_DOMAIN[0]

    migrator = PostgresqlMigrator(db.database)

    with db.database.transaction():
        Organization.create_table()
        if settings.GOOGLE_APPS_DOMAIN:
            domain = settings.GOOGLE_APPS_DOMAIN[0]
        else:
            domain = None

        default_org = Organization.create(name="Default", settings={}, domain=domain)

        column = Group.org
        column.default = default_org

        migrate(
            migrator.add_column('groups', 'org_id', column),
            migrator.add_column('events', 'org_id', column),
            migrator.add_column('data_sources', 'org_id', column),
            migrator.add_column('users', 'org_id', column),
        )

    db.close_db(None)

