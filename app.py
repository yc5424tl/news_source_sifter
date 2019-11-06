from sifter import create_app
import os

app = create_app()
app.config['SQLALCHEMY_DATABSE_URI'] = os.getenv('NEWS_SRC_MS_DB_URL')
app.app_context().push()

from sifter.models import Source, Category

@app.shell_context_processor
def make_shell_context():
    return {'db': app.db, 'Source': Source, 'Category': Category}