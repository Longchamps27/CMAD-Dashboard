import dash
import plotly.graph_objects as go
from dash import html
from dash import dcc
from sqlalchemy import Column, Integer, Float, Date
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import exc
import pandas as pd
from dash.dependencies import Input, Output

#Data de la conección SQL
user = 'Usuario'
password = 'Password'
host = 'localhost'
port = '3306'
database = 'CMA'

#Query que para leer la información de la base de datos
query = "LOAD DATA LOCAL INFILE '/path/to/file/CMA.csv' INTO TABLE CMA_Data FIELDS TERMINATED BY ',' OPTIONALLY ENCLOSED BY '' ESCAPED BY '' LINES TERMINATED BY '\\n';"

#Conectarse a la base de datos y devolver el objeto "engine" de SQLAlchemy 
def get_connection():
    return create_engine(
        'mysql+pymysql://{0}:{1}@{2}:{3}/{4}?local_infile=1'.format(user, password, host, port, database), echo=True
    )

try:
	engine = get_connection()
	#Crea la base de datos CMA si no existe
	engine.execute('CREATE DATABASE IF NOT EXISTS CMA;')
	print('Database is created')
	engine.execute('USE CMA;')
	record = engine.execute('SELECT DATABASE();')
	print('You are connected to database: ', record)
	print('Creating table....')
	#Crea la tabla en la cual se cargará la base de datos
	engine.execute('CREATE TABLE IF NOT EXISTS CMA_Data( ExchangeID varchar(255), CountryIDState varchar(255), CountryIDCode int(11),  Year int(11), Region int(11), CMAPresence int(11), Client int(11), SpecificClient int(11), ClientName varchar(255), ForT int(11), Consumer int(11), ConsumerName varchar(255), CompOrigin int(11), CompOrCode varchar(255), AgentID varchar(255), OperatorOrigin int(11), Service int(11), AgentStructure int(11), OwnershipStructure int(11), CountryISOCode char(3), CountryName varchar(255));')
	print('Table is created')
	print('Inserting records....')
	engine.execute(query)
except exc.SQLAlchemyError as e:
	print('Error while connecting to MySQL', e)

#Colores usados
colors = {
    'background': '#181c1c',
    'text': '#7FDBFF'
}

# Inicializa la aplicación Dash
app = dash.Dash(__name__)

#Query que devuelve el total de contratos de los 10 clientes mas grandes
query1 = ('select ClientName, count(*) as Total from CMA_Data where ClientName <> "-1" group by ClientName order by Total desc limit 10;')

#Query que devuelve el total de contrato por año entre 1980 y 2016
query2 = ('select Year, count(*) as Total from CMA_Data group by Year order by Total desc; ')

#Query que devuelve el total de contratos en cada pais entre 1908 y 2016
query3 = ('select CountryISOCode, CountryName, count(*) as Contratos from CMA_Data group by CountryISOCode, CountryName;')

df1 = pd.read_sql(query1, engine)

df2 = pd.read_sql(query2, engine)

df3 = pd.read_sql(query3, engine)

fig1 = go.Figure(
	data = [go.Bar(name = 'Totales', x=df1.ClientName, y=df1.Total, marker = dict(color = df1.loc[:,'Total'], colorscale = 'oryel'))]

)

fig2 = go.Figure(
	data = [go.Bar(name = 'Totales', x=df2.Year, y=df2.Total, marker = dict(color = df2.loc[:,'Total'], colorscale = 'solar'))]

)

fig3 = go.Figure(
	data = go.Choropleth(
		locations = df3.CountryISOCode, z = df3.Contratos, text = df3.CountryName, colorscale = 'Blues', autocolorscale = False, reversescale = True, 			marker_line_color = 'darkgray', marker_line_width = 0.5, colorbar_title = 'Número de contratos')
)


fig1.update_layout(
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font_color = colors['text']
)

fig2.update_layout(
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font_color = colors['text']
)

fig3.update_layout(
    plot_bgcolor = colors['background'],
    paper_bgcolor = colors['background'],
    font_color = colors['text']
)

#layout del dashboard
app.layout = html.Div (style={'backgroundColor': colors['background']}, children = [
	html.Div([
		html.H1(children = 'Número de contratos por cliente', style = {'textAlign' : 'center', 'color' : colors['text']}),
		dcc.Graph(id = 'graph1', figure = fig1, style={'display': 'inline-block'})
	]),
	html.Div([
		html.H1(children = 'Número total de contratos por año', style = {'textAlign' : 'center', 'color' : colors['text']}),
		dcc.Graph(id = 'graph2', figure = fig2, style={'display': 'inline-block'})
	]),
	html.Div ([
		html.H1 (children = 'Número total de contratos en paises en conflicto', style = {'textAlign' : 'center', 'color' : 				colors['text']}),
		dcc.Graph(id = 'graph3', figure = fig3)
	])
])

if __name__ == '__main__':
	app.run_server(debug=True)
