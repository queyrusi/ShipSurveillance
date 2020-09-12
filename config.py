# Create global chart template
TOKEN = 'pk.eyJ1IjoiamFja2x1byIsImEiOiJjajNlcnh3MzEwMHZtMzNueGw3NWw5ZXF5In0.fk8k06T96Ml9CLGgKmk81w'

LAYOUT = dict(autosize=True,
              automargin=True,
              margin={
                  'l': 0,
                  't': 0,
                  'b': 0,
                  'r': 0
              },
              hovermode="closest",
              plot_bgcolor="#F9F9F9",
              paper_bgcolor="#F9F9F9",
              legend=dict(font=dict(size=10), orientation='h'),
              title='Visualization',
              mapbox=dict(
                  accesstoken=TOKEN,
                  style="light",
                  center=dict(lon=4, lat=52),
                  zoom=2,
              ))

DATAPATH = "data/location/LOCATION.json"
DATERANGE = 60
