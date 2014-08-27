<<<<<<< HEAD
import os
from project import app

port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
=======
from app.views import app

app.run(debug=True)
>>>>>>> 4a19f85f75cb5013e7c7d72ca685d6f61b254e0c
