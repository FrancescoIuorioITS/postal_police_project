<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Postal Police project</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
        }
        h1, h2, h3 {
            color: #333;
        }
        pre {
            background-color: #f4f4f4;
            padding: 10px;
            border: 1px solid #ddd;
            overflow-x: auto;
        }
        code {
            background-color: #f4f4f4;
            padding: 2px 4px;
            border-radius: 4px;
        }
        .badge {
            display: inline-block;
            padding: 10px;
            margin: 5px;
            color: #fff;
            text-align: center;
            border-radius: 5px;
        }
        .neo4j { background-color: #008cc1; }
        .python { background-color: #FFD43B; color: #333; }
        .geopy { background-color: #66CC33; }
        .dotenv { background-color: #E34F26; }
        .faker { background-color: #FF70A6; }
        .center {
            text-align: center;
        }
    </style>
</head>
<body>

<h1 id="readme-top">📡 Postal Police Project</h1>

<p>
    Questa applicazione fornisce una serie di strumenti per creare e gestire dati in un database Neo4j per tracciare attività criminali. 
    L'applicazione supporta funzionalità come la creazione di utenti, la generazione di celle, la creazione di connessioni tra telefoni e celle, 
    e il recupero di dati dal database.
</p>

<h2>Indice</h2>
<ul>
    <li><a href="#Requisiti">Requisiti</a></li>
    <li><a href="#Installazione-e-configurazione">Installazione e configurazione</a></li>
    <li><a href="#Utilizzo">Utilizzo</a></li>
    <li><a href="#Licenza">Licenza</a></li>
</ul>

<h2 id="Requisiti">Requisiti</h2>
<p>
    Per avviare l'applicazione, è necessario/preferibile avere:
</p>
<ul>
    <li><strong>Python 3.6 o superiore</strong></li>
    <li><strong>Database Neo4j</strong></li>
    <li><strong>Le seguenti librerie Python</strong>:
        <ul>
            <li><code>neo4j</code></li>
            <li><code>geopy</code></li>
            <li><code>python-dotenv</code></li>
            <li><code>faker</code></li>
        </ul>
    </li>
</ul>
<p align="right">(<a href="#readme-top">torna in cima</a>)</p>

<h2 id="Installazione-e-configurazione">Installazione e configurazione</h2>

<h3>1. Clona la repository:</h3>
<p>
    Apri il terminale e vai nella directory dove vuoi clonare il repository tramite <code>cd 'yo/ur/path'</code><br>
    Esegui il seguente comando:
</p>
<pre><code>git clone https://github.com/FrancescoIuorioITS/postal_police_project.git</code></pre>

<h3>2. Crea un ambiente virtuale e attivalo:</h3>
<pre><code>python -m venv venv
source venv/bin/activate  # Su Windows, usa `venv\Scripts\activate`</code></pre>


<p align="right">(<a href="#readme-top">torna in cima</a>)</p>



<h2 id="Utilizzo">Utilizzo</h2>

<h3>DataCleaner</h3>
<p>La classe <code>DataCleaner</code> fornisce metodi per eliminare vari tipi di nodi e relazioni dal database.</p>
<pre><code>from db_connection import with_database

@with_database
class DataCleaner:
    # Metodi per eliminare dati dal database</code></pre>

<h3>CriminalTrackingApp</h3>
<p>La classe <code>CriminalTrackingApp</code> include metodi per tracciare la posizione degli individui e trovare sospetti in base alle loro connessioni cellulari.</p>
<pre><code>from db_connection import Neo4jConnector

class CriminalTrackingApp:
    # Metodi per trovare la posizione di una persona e sospetti</code></pre>

<h3>UserCreationApp</h3>
<p>La classe <code>UserCreationApp</code> è responsabile della creazione di utenti e dell'assegnazione di numeri di telefono a questi ultimi.</p>
<pre><code>from db_connection import with_database

@with_database
class UserCreationApp:
    # Metodi per creare utenti e aggiungere numeri di telefono</code></pre>

<h3>CellCreationApp</h3>
<p>La classe <code>CellCreationApp</code> genera celle per diverse città in Italia.</p>
<pre><code>from db_connection import with_database

@with_database
class CellCreationApp:
    # Metodi per creare celle</code></pre>

<h3>ConnectionCreationApp</h3>
<p>La classe <code>ConnectionCreationApp</code> gestisce la creazione di connessioni tra telefoni e celle.</p>
<pre><code>from db_connection import with_database

@with_database
class ConnectionCreationApp:
    # Metodi per creare connessioni tra telefoni e celle</code></pre>

<h3>DataRetrievalApp</h3>
<p>La classe <code>DataRetrievalApp</code> fornisce metodi per recuperare dati dal database.</p>
<pre><code>from db_connection import with_database

@with_database
class DataRetrievalApp:
    # Metodi per recuperare dati dal database</code></pre>

<h3>Esempio di Utilizzo</h3>
<pre><code>if __name__ == "__main__":
    with UserCreationApp() as user_creation, 
         CellCreationApp() as cell_creation, 
         DataRetrievalApp() as retrieval_app, 
         ConnectionCreationApp(retrieval_app) as connection_creation:
         
        user_creation.generate_fake_people(7500)
        all_people = retrieval_app.get_all_people()
        print(f"Totale persone create: {len(all_people)}")

        cell_creation.generate_cells_for_italy(total_cells=1000, ratio_5g=0.3)
        all_cells = retrieval_app.get_all_cells()
        print(f"Totale celle create: {len(all_cells)}")

        connection_creation.generate_fake_connections(25000)
        all_connections = retrieval_app.get_all_connections()
        print(f"Totale connessioni create: {len(all_connections)}")

    print("Operazioni sul database completate e risorse chiuse correttamente.")</code></pre>

<p align="right">(<a href="#readme-top">torna in cima</a>)</p>


</body>
</html>
