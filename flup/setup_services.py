import click
from flup import app, db

@app.cli.command()
def create_db():
    click.echo('Create the DB (None if the DB already exists.)')
    db.create_all()

@app.cli.command()    
def recreate_db():
    click.echo('Drop the current DB and recreate it')
    db.drop_all()
    db.create_all()
