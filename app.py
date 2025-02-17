from flask import Flask, request, render_template
from rdflib import Graph, URIRef, Namespace, Literal

app = Flask(__name__)

g = Graph()
g.parse('mytourism.owl', format='xml')

ns = Namespace("http://www.my_ontology.edu/mytourism#")

# คำแปลของ Predicate ตามภาษา
predicate_translations = {
    'hasFlower': {'th': 'ดอกไม้ประจำจังหวัด', 'en': 'Flower'},
    'hasImageOfProvince': {'th': 'ชื่อรูปภาพของจังหวัด', 'en': 'Image Of Province'},
    'hasLatitudeOfProvince': {'th': 'พิกัดละติจูดของจังหวัด', 'en': 'Latitude'},
    'hasLongitudeOfProvince': {'th': 'พิกัดลองจิจูดของจังหวัด', 'en': 'Longitude'},
    'hasMotto': {'th': 'คำขวัญของจังหวัด', 'en': 'Motto'},
    'hasNameOfProvince': {'th': 'ชื่อจังหวัด', 'en': 'Name Of Province'},
    'hasSeal': {'th': 'สัญลักษณ์ประจำจังหวัด', 'en': 'Seal'},
    'hasTraditionalNameOfProvince': {'th': 'ชื่อเดิมของจังหวัด', 'en': 'Traditional Name Of Province'},
    'hasTree': {'th': 'ต้นไม้ประจำจังหวัด', 'en': 'Tree'},
    'hasURLOfProvince': {'th': 'ชื่อเว็บไซต์ของจังหวัด', 'en': 'URL Of Province'}
}

@app.route('/', methods=['GET', 'POST'])
def search_province():
    results = set()  # ใช้ set เพื่อป้องกันการซ้ำ
    province_name = ""  # ตัวแปรสำหรับเก็บชื่อจังหวัด
    lang = request.form.get('lang', request.args.get('lang', 'th'))
    
    if request.method == 'POST':
        query = request.form['query'].lower()
        
        # ค้นหาจังหวัดจาก ontology
        for s, p, o in g:
            if isinstance(s, URIRef) and ns.ThaiProvince in g.objects(s, None):
                # หากพบจังหวัดที่ตรงกับคำค้น
                if query in str(s).lower() or query in str(o).lower():
                    # ตรวจสอบชื่อจังหวัดจาก hasNameOfProvince
                    for pred, obj in g.predicate_objects(s):
                        if pred == ns.hasNameOfProvince and isinstance(obj, Literal):
                            if obj.language == lang or not obj.language:
                                province_name = obj
                    # เพิ่มข้อมูลของจังหวัดที่พบ
                    for pred, obj in g.predicate_objects(s):
                        # ตรวจสอบว่า predicate เป็นค่าที่เกี่ยวข้องกับจังหวัด
                        if pred != ns.type and pred != URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#type"):
                            # แปลคำ predicate เป็นภาษาไทยหรือภาษาอังกฤษ
                            pred_name = pred.split('#')[-1]
                            if pred_name in predicate_translations:
                                translated_pred = predicate_translations[pred_name].get(lang, pred_name)
                            else:
                                translated_pred = pred_name
                            
                            # ตรวจสอบ obj ว่ามี xml:lang หรือ rdf:datatype
                            if isinstance(obj, Literal):
                                # หาก obj เป็น Literal เราจะตรวจสอบว่าเป็นภาษาใด
                                if obj.language == lang or not obj.language:
                                    # เพิ่มค่าลงใน set เพื่อไม่ให้ซ้ำ
                                    results.add(f"{translated_pred} : {obj}")
                            else:
                                # หาก obj ไม่ใช่ Literal แสดงค่าปกติ
                                results.add(f"{translated_pred} : {str(obj)}")
        
        # ถ้าไม่พบผลลัพธ์
        if not results:
            results.add("ไม่พบข้อมูลจังหวัดนี้" if lang == 'th' else "Province details not found")

    return render_template('index01.html', results=sorted(results), province_name=province_name, lang=lang, current_lang=lang)

if __name__ == '__main__':
    app.run(debug=False)