import rdflib
import os
from flask import render_template, flash
from app import app
from provstore.api import Api
from app.models import ArtID
from app.forms import QueryForm



api = Api(base_url='https://openprovenance.org/store/api/v0', username="kym3ni",
          api_key="ef2cff88eb50f915a5fd6653e19392b355ca5c0a")

location = """SELECT DISTINCT ?y
                WHERE
                    {
                        {?x art:location ?y.} UNION 
                        {?x gallery:location ?y.} UNION 
                        {?x transport:destination ?y.}
                    }"""

specialist = """SELECT DISTINCT ?y
                WHERE
                    {
                        ?w auction:specialistname ?y.
                        ?w auction:specialistdob ?x.
                        ?w auction:specialistgender ?z.
                    }"""

hammerprice = """SELECT DISTINCT ?y
                WHERE
                    {
                        ?x auction:hammerprice ?y.
                    }"""

auctionhouse = """SELECT DISTINCT ?y
                WHERE
                    {
                        ?x auction:auctionhouse ?y.
                    }"""

gallery = """SELECT DISTINCT ?y
                WHERE
                    {
                        ?x gallery:name ?y.
                        ?x gallery:owner ?z.
                    }"""

buyer = """SELECT DISTINCT ?y
                WHERE
                    {
                        ?w auction:purchasername ?y.
                        ?w auction:purchaserdob ?x.
                        ?w auction:purchasergender ?z.
                    }"""

@app.route('/queries', methods=['GET', 'POST'])
def runQuery():
    form = QueryForm()
    results = []
    if form.validate_on_submit():
        querytype = form.querytype.data
        prov_docdb = ArtID.query.filter_by(artname=form.artname.data).first()
        if prov_docdb is None:
            flash('There is no provenance for this artwork')
        else:
            prov_doc = api.document.get(prov_docdb.docid)
            provn_doc = prov_doc.prov
            currentdir = os.getcwd()
            filename = form.artname.data.replace(" ", "")
            outputfile = currentdir+'/app/rdfqueryfiles/'+filename+'.rdf'
            provn_doc.serialize(outputfile, format='rdf', rdf_format='ttl')
            querystr = ""
            if querytype == 'location':
                querystr = location
            elif querytype == 'specialist':
                querystr = specialist
            elif querytype == 'hammerprice':
                querystr = hammerprice
            elif querytype == 'auctionhouse':
                querystr = auctionhouse
            elif querytype == 'gallery':
                querystr = gallery
            elif querytype == 'buyer':
                querystr = buyer
            g = rdflib.Graph()
            g.parse(outputfile, format='n3')
            qres = g.query(querystr)
            for row in qres:
                results.append(row)
    return render_template('query.html', title='Queries', form=form, results=results)

