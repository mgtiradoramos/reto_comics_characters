from flask import Flask,render_template,make_response, jsonify,request
import requests

app = Flask (__name__)

PORT = 5001
HOST = '0.0.0.0'


@app.route("/searchComics",methods=["POST"]) 
def listaMarvel():

    req = request.get_json()

    if 'tipobusqueda' not in req:
        res = make_response(jsonify({"error":"Falta el parametro tipobusqueda"}),400)
        return res

    if  req['tipobusqueda'].strip() == "" or (req['tipobusqueda'] != "characters" and req['tipobusqueda'] != "comics"):
        res = make_response(jsonify({"error":"El parametro tipobusqueda  debe ser characters o comics"}),400)
        return res  
 
    url,validacion = armarUrl(req) 

    if validacion != "":
        return make_response(jsonify({"error":validacion}),400)  

    print(url)      
    response = requests.get(url)
    item = []

    if response.status_code == 200:
        data = response.json()
        results = data['data']['results']
        items=[]

        if req['tipobusqueda'] == "character":
            for e in results:
                item = {
                'id': e['id'],
                'name': e['name'],
                'image':e['thumbnail']['path'] +"." + e['thumbnail']['extension'],
                'apearances':e['comics']['available']
                }

                items.append(item)
        else:
            dateOnSaleDate = ""
            for e in results:
                for date in e['dates']:
                    if date['type'] == "onsaleDate":
                        dateOnSaleDate = date['date']
                item = {
                'id': e['id'],
                'title': e['title'],
                'image':e['thumbnail']['path'] +"." + e['thumbnail']['extension'],
                'onSaleDate':dateOnSaleDate
                }

                items.append(item)

        return jsonify(results = items)
         
    return make_response(jsonify({"error":"Problemas al consutar servicio de Marvel"}),400) 
    
   


def armarUrl(req):


        tipoBusqueda = req['tipobusqueda']

        url="https://gateway.marvel.com:443/v1/public/"+tipoBusqueda+"?apikey=cb4fb7d6398e0d7f94f961f1138705a0&hash=aad5254291b925b12d9ffdf8867e62c7&ts=1&limit=20"
        res = ""

        if 'startsWith' not in req and 'name' not in req:
            res = "Falta el parametro startsWith"
            return url,res

        if  req['startsWith'].strip() == "" and 'name' not in req:
            res = "El parametro startsWith no debe venir vacio"
            return url,res 
        else:
            if tipoBusqueda == "character":
                url = url + "&nameStartsWith=" + req['startsWith']
            else:
                url = url + "&titleStartsWith=" + req['startsWith']   

        if 'offset' not in req:
            res = "Falta el parametro offset"
            return url,res

        if  req['offset'] == "" :
            res = "El parametro offset no debe venir vacio"
            return url,res
        else:
            url = url + "&offset=" + str(req['offset'])    

        if 'name' in req and req['name'].strip() != "":
            if tipoBusqueda == "character":
                url = url + "&name=" + req['name'] 
            else:
                url = url + "&title=" + req['name']     

        return url,res       


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)



