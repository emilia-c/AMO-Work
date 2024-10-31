import wayback
import datetime

client = wayback.WaybackClient()
for record in client.search('http://nasa.gov', to_date=(1999, 1, 1)):
    memento = client.get_memento(record)

print(memento)