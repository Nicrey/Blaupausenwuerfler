# Blaupausenwürfler
Flask App, die aus einem Data Folder Tabellen/Generatoren ausliest und auf diese würfelt.
Die App liest alle Dateien aus dem in der Umgebungsvariable "BW_DATA_FOLDER" definierten Verzeichnis aus und versucht sie als Tabellen oder Generatoren zu importieren.
<br>Alle Dateien, deren Name nicht mit "Generator" oder "Multigenerator" anfängt, werden als normale Tabellen interpretiert. 

## Tabellen
Einfachste Form der Zufallstabelle. Man würfelt und hat ein Ergebnis und das wars. 
### Layout
> -------------File Begin-------------<br>
> URL/Link zu kompletter Tabelle<br>
> Name der Tabelle (meist 1WX ...)<br>
> Idee: Name des Ideengebers<br>
> Autor:innen: Namen der Autor:innen<br>
> Würfeltyp im Format: 1WX (z.B. 1W10)<br>
> Tabelleneinträge im Format: Würfelergebnis~~~Tabellenwert<br>
> -------------File End----------------

#### Beispiel
> http://blaupausen.system-matters.de/2018/08/09/1w6-dinge-die-im-bart-des-riesen-zu-finden-sind/
> <br>1W6 Dinge, die im Bart des Riesen zu finden sind
> <br>
> <br>Autor:innen: Lukas, Moonmonth, Midnighter
> <br>1W6
> <br>1~~~ 1. Hier leben 1W4 Goblins mit dem Riesen in einer Symbiose. Sie pflegen ihn und genießen seinem Schutz.
> <br>2~~~ 2. Man sagt, der Bart eines Riesen enthalte genug eingetrocknete Nahrung für Wochen. Das stimmt nicht ganz – es finden sich lediglich 1W6 Rationen von > besorgniserregender – aber durchaus genießbarer – Qualität
> <br>3~~~ 3. Zwei Gnome leben hier, die dem Riesen zuflüstern, wohin er laufen soll. Sie wohnen auch im Bart und transportieren so ihren gewaltigen Goldschatz
> <br>4~~~ 4. Die lang vergessenen, sterblichen Überreste eines allzu tapferen Ritters in voller Plattenrüstung, nebst ebenso skelettierten Streitross. Würfle 1W4: Bei einer 1 sind die ruhelosen Geister von Ross und Reiter immer noch hier und erzählen ihre heroische, aber tragische Geschichte
> <br>5~~~ 5. Das Wrack einer gnomischen Flugmaschine. Zwei der drei Besatzungsmitglieder sind in ihren Sitzen zerquetscht worden, dem dritten ist offenbar die Flucht – oder der Absprung – gelungen. Die Energiequelle des Antriebs könnte noch funktionstüchtig sein, außerdem findet sich eine große versiegelte Kiste an Bord.
> <br>6~~~ 6. Ein Nest voller Wolkenhaie (3W4). Diese flinken geflügelten Fleischfresser picken dem Riesen normalerweise die Essensreste aus den Zähnen, schrecken aber auch nicht vor waghalsigen Abenteurern zurück, die sich auf ihre Höhe verirrt haben.

## Generatoren
Generatoren sind eine Sammlung an Tabellen, die auch untereinander sich referenzieren können und einer Syntaxregelung, um richtige Grammatik zu gewährleisten.
<br>Beispiel: Ein grammatikalisch korrekter Abenteuertitelgenerator (siehe unten)
<br>Der Dateiname sollte mit Generator anfangen, damit er automatisch richtig geladen wird.
### Layout
> -------------File Begin-------------<br>
> URL/Link zum vollständigen Generator<br>
> Name des Generators (meist Zufallsgenerator: ...)<br>
> Idee: Name des Ideengebers<br>
> Autor:innen: Namen der Autor:innen<br>
> [Modifier Hierarchy]<br>
> [Syntax Tabelle]<br>
> [Tabellen und Lookups]<br>
> -------------File End----------------
#### Syntax Tabelle
Die Haupttabelle des Generators, die über das Aussehen des Outputs entscheidet.

> ----------Anfang der Tabelle-------------
> <br>\###Syntax
> <br>Würfeltyp im Format: 1WX (z.B. 1W20)
> <br>Einträge im Format: Würfelwert~~~Eintrag
> <br>---------Ende der Tabelle-------------

Einträge in der Syntaxtabelle, können andere Tabellen referenzieren, Modifizierungen vornehmen oder Alternativen festlegen.
* [Tabellenname] referenziert eine andere Tabelle
* [Tabellenname~Modifizierer] modifiziert eine Tabelle mit einem Modifizierer (ein Zeichen lang)
* [Tabellenname->] verweist die Tabelle darauf, dass sie Modifizierer einer benachbarten Tabelle nehmen soll
* -> kann auch weiter entfernte Tabellen nachschauen mit z.B. ->>> (3 nach rechts)
* -> kann auch in die andere Richtung schauen mit z.B. -<< (2 nach links)
* ||| Modifizierer [Tabellenname1],[Tabellenname2],... definiert Alternativen, die gleichzeitig ausgegeben werden, wobei jede Kombination der Tabellen mit dem Modifizierer versehen wird.

<b>Anwendungsbeispiel:</b><br>
Einen Abenteuertitel der Syntax "Die Burg des grauen Herrschers" generieren:

> [Artikel->] [Nomen] [Artikel\~G->>] [Adjektiv\~G->] [Nomen\~G] ||| P [Nomen], [Nomen~G]

* [Artikel->] ist eine Lookuptabelle, die nur einen Artikel nachschaut und zwar basierend auf der Tabelle eins rechts daneben
* [Nomen] würfelt ein zufälliges Nomen aus
* [Artikel\~G->>] schaut einen Artikel nach, basierend auf der Tabelle zwei rechts daneben, und nimmt die modifizierte Version (G für Genitiv)
* [Adjektiv\~G->] würfelt ein Adjektiv aus und passt es an die Tabelle eins rechts daneben an 
* [Nomen\~G] würfelt ein Nomen aus und passt es in den Genitiv an
* ||| P [Nomen], [Nomen\~G] führt dazu, dass noch 3 weitere Ausführungen generiert werden, wo jeweils eine oder beide der Nomen mit dem Plural-Modifizierer versehen wird

#### Tabellen
Damit die obige Syntax funnktioniert, sind die Tabellen etwas anders aufgebaut als normale Tabellen.

> ----------Anfang der Tabelle-------------
> <br>\###Tabellenname
> <br>Würfeltyp im Format: 1WX (z.B. 1W20)
> <br>Einträge im Format: Würfelergebnis~~~Eintrag
> <br>---------Ende der Tabelle-------------

Einträge sind dabei wie normal aufgebaut, nur können sie auch modifizierte Werte beinhalten.
* Diese werden in eckigen Klammern eingetragen [Modifizierer: Modifizierter Eintrag]
* Andere Tabellen können in geschweiften Klammern referenziert werden {Adjektiv}
* Ein Modifizierer, der für andere Tabellen interessant sein könnte, kann am Ende angehängt werden mit: ***M (zum Beispiel für den Artikel)

Zum Beispiel die Nomentabelle mit den Alternativversionen für Genitiv und Plural:
> \###Nomen
> <br>1W3
> <br>1~\~\~Burg [G: Burg][P: Burgen]\***W
> <br>2~\~\~Wald [G: Waldes] [P:Wälder]\***M
> <br>3~\~\~Herrscher [G:Herrschers] [P:Herrscher]\***H

#### Lookuptabellen
Lookuptabellen funktionieren ähnlich wie Tabellen, nur das sie nicht würfeln, sondern direkt Modifizierer nachschauen

> ----------Anfang der Tabelle-------------
> <br>\|||Tabellenname
> <br>Einträge im Format: Modifizierer~~~Eintrag
> <br>---------Ende der Tabelle-------------

Beispiel für eine Artikeltabelle mit den Modifizierern M (Männlich),W (Weiblich) ,S (Sächlich) und G(Genitiv):
> |||Art
> <br>M~\~\~der
> <br>W~\~\~die
> <br>S~\~\~das
> <br>MG~\~\~des
> <br>WG~\~\~der
> <br>SG~\~\~des

#### Modifizierer Hierarchy
Dient dazu die Modfizierer zu priorisieren. 
Das dient dazu, dass wenn mehrere Modfizierer für eine Tabelle relevant sind
 (z.B. G für Genitiv und P für Plural) und es keinen Eintrag für die Kombination (PG:) gibt, wird
 wenn es Einträge für G und P gibt, der Eintrag genommen, dessen Modifizierer höher gewertet ist. 
 
>  ----------Anfang der Hierarchie-------------
> <br>***Modifier Hierarchy
> <br>Modifizierer1>Modifizierer2>Modifizierer3...
> <br>---------Ende der Hierarchie3-------------

Beispiel für obige Tabelle:
> ***Modifier Hierarchy
> <br>M>W>S>P>G

In dem Fall wird im Plural und Genitiv Fall immer der Pluraleintrag genommen.

#### Generator-Beispiel
Beispiel für einen Abenteuertitelgenerator:

> http://blaupausen.system-matters.de/2019/07/06/zufallsgenerator-abenteuer-titel/
> <br>Zufallsgenerator: Abenteuer(-Titel)
> <br>Idee: Pixellance
> <br>Autor:innen: Pixellance, Lukas, Moonmoth, Tegres
> <br>\*\*\*Modifier Hierarchy
> <br>M>W>S>P>G>N
> <br>\###Syntax
> <br>1W3
> <br>1~\~\~[Art->] [A] [Art\~G->] [C\~G] ||| P [A],[C\~G]
> <br>2~\~\~[Art->>] [W3] [A-<]
> <br>3~\~\~[Art->] [C] [Art\~G->>] [B\~G->] [A\~G] ||| P [C], [A\~G]
> <br>\###A
> <br>1W3
> <br>1~\~\~Burg[P:Burgen]\*\*\*W
> <br>2~\~\~Verlies[G:Verlieses][P:Verliese]\*\*\*S
> <br>3~\~\~Labyrinth[G:Labyrinths][P:Labyrinthe]\*\*\*S
> <br>\###B
> <br>1W3
> <br>1~\~\~rot[N:rote][G:roten][P:roten]
> <br>2~\~\~grün[N:grüne][G:grünen][P:grünen]
> <br>3~\~\~blau[N:blaue][G:blauen][P:blauen]
> <br>\###C
> <br>1W3
> <br>1~\~\~Abenteuer[G:Abenteuers]\*\*\*S
> <br>2~\~\~Gefahr[P:Gefahren]\*\*\*W
> <br>3~\~\~Held[P:Helden][G:Helden]\*\*\*M
> <br>\###W3
> <br>1W3
> <br>1~\~\~eine
> <br>2~\~\~zwei\*\*\*P
> <br>3~\~\~drei\*\*\*P
> <br>|||Art
> <br>M~\~\~der
> <br>W~\~\~die
> <br>S~\~\~das
> <br>MG~\~\~des
> <br>WG~\~\~der
> <br>SG~\~\~des
> <br>MP~\~\~die
> <br>WP~\~\~die
> <br>SP~\~\~die
> <br>MPG~\~\~der
> <br>WPG~\~\~der
> <br>SPG~\~\~der

Beispielergebnisse:
* Die Burg der Gefahr, Alternativen: Die Burgen der Gefahr, Die Burg der Gefahren, Die Burgen der Gefahren
* Die drei Verliese
* Das Labyrinth des grünen Helden, Alternativen: ...

### Andere Tabellen und Generatoren importieren
Generatoren erlauben es außerdem andere bereits geladene Generatoren und Tabellen zu laden, um diese zu integrieren.
<br> Importe sind im gleichen Abschnitt wie Tabellen zu platzieren.
<br> Damit eine Datei im letzten Schritt geladen wird, um vorher geladene Tabellen zu importieren, sollte der Name mit MultiGenerator anfangen.


> §§§Referenzname
> <br>Name des Generators

Beispiel:
> §§§Abenteuertitel
> <br>Zufallsgenerator: Abenteuertitel

Jetzt kann in der Syntaxtablle mit [Abenteuertitel] ein zufälliger Wurf auf dem Zufallsgenerator eingebunden ist.
