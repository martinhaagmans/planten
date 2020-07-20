import os
import sys
import json
import logging
import sqlite3

from pathlib import Path

from flask import Flask
from flask import flash
from flask import redirect
from flask import url_for
from flask import jsonify
from flask import request
from flask import make_response
from flask import render_template

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = 'uploads'

dir_path = os.path.dirname(os.path.realpath(__file__))
DATABASE = os.path.join(dir_path, 'static', 'planten.sqlite')
PICS = os.path.join(dir_path, 'static', 'img')

class AddPlant:
    def __init__(self, name_lat):
        self.conn = sqlite3.connect(DATABASE)
        self.c = self.conn.cursor()
        self.name_lat = name_lat

    def __del__(self):
        self.conn.close()

    def execute_sql(self, sql):
        try:
            self.c.execute(sql)
        except sqlite3.IntegrityError as e:
            print(e)
        else:
            self.conn.commit()
        return

    def write_names(self, name_reg):
        sql = f"""INSERT INTO namen 
            (NAAM, LAT_NAAM)
            VALUES('{name_reg}', '{self.name_lat}')
            """
        self.execute_sql(sql)
        return

    def parse_height(self, height):
        height_minmax = dict()
        height_minmax['zeerlaag'] = (0, 30)
        height_minmax['laag'] = (30, 79)
        height_minmax['middelhoog'] = (80, 139)
        height_minmax['hoog'] = (140, 200)
        height_minmax['zeerhoog'] = (201, 99999999999)
        return height_minmax[height]

    def parse_width(self, width):
        width_minmax = dict()
        width_minmax['smalst'] = (0, 25)
        width_minmax['smal'] = (25, 49)
        width_minmax['breed'] = (50, 100)
        width_minmax['breedst'] = (101, 99999999999)
        return width_minmax[width]

    def write_size(self, height, width):
        if height is None and width is None:
            sql = f"""INSERT INTO afmetingen
                (LAT_NAAM)
                VALUES ('{self.name_lat}')
                """
        elif height is not None and width is None:
            height_min, height_max = self.parse_height(height)
            sql = f"""INSERT INTO afmetingen
                (LAT_NAAM, MIN_HOOGTE, MAX_HOOGTE, HOOGTE)
                VALUES ('{self.name_lat}', 
                {height_min}, {height_max},'{height}')
                """
        elif height is None and width is not None:
            width_min, width_max = self.parse_width(width)
            sql = f"""INSERT INTO afmetingen
                (LAT_NAAM,MIN_BREEDTE, MAX_BREEDTE, BREEDTE)
                VALUES ('{self.name_lat}', 
                {width_min}, {width_max},'{width}')
                """
        elif height is not None and width is not None:
            height_min, height_max = self.parse_height(height)
            width_min, width_max = self.parse_width(width)
            sql = f"""INSERT INTO afmetingen
                (LAT_NAAM, MIN_HOOGTE, MAX_HOOGTE, HOOGTE,
                MIN_BREEDTE, MAX_BREEDTE, BREEDTE)
                VALUES ('{self.name_lat}', 
                {height_min}, {height_max},'{height}',
                {width_min}, {width_max},'{width}')
                """
        self.execute_sql(sql)
        return

    def get_arch_options(self):
        return 'lij bg ho bp op sp ve kr pol mat zode'.split()

    def get_color_options(self):
        return 'wit roze geel oranje rood paars lila groen zwart'.split()

    def get_months(self):
        return 'jan feb mrt apr mei jun jul aug sep okt nov dec'.split()

    def get_structure(self):
        return 'kort med lang'.split()

    def get_langlevend(self):
        return 'md5 md10 per ll'.split()

    def get_uitbreiding(self):
        return 'geen zeerbep langzaam matig snel'.split()

    def get_persistentie(self):
        return 'zlaag laag middel hoog'.split()

    def get_uitzaaiend(self):
        return 'min matig hoog'.split()
    
    def get_licht(self):
        return 'zon halfschaduw schaduw'.split()

    def get_grondsoort(self):
        return 'nat vochtig droog zeervrucht onvrucht'.split()
        
    def get_vermeerderen_options(self):
        return 'stek afleg scheur uitlop zaai'.split()

    def parse_options_to_bool(self, user_input, options):
        out = dict()
        for opt in options:
            if opt in user_input:
                out[opt] = str(1)
            else:
                out[opt] = str(0)
        return out

    def write_architectuur(self, architectuur):
        arch_options = self.get_arch_options()
        arch_out = self.parse_options_to_bool(architectuur, arch_options)
        sql_columns = ', '.join(arch_options)
        sql_values = [arch_out[val] for val in arch_options]
        sql_values = ', '.join(sql_values)
        sql = f"""INSERT INTO architectuur (LAT_NAAM, {sql_columns})
            VALUES ('{self.name_lat}', {sql_values})
            """
        self.execute_sql(sql)
        return

    def write_algemeen(self, blad, planten_per_m, soort, piet, winterhard,
                       insecten, makkelijk, inheems, wintergroen, opmerkingen,
                       opmerkingen_piet, opmerkingen_verzorging):

        sql = f"""INSERT INTO algemeen 
            (LAT_NAAM) VALUES ('{self.name_lat}')"""
        self.execute_sql(sql)

        if blad is not None:
            sql = f"""UPDATE algemeen 
                SET BLAD = '{blad}'
                WHERE LAT_NAAM='{self.name_lat}' 
                """
            self.execute_sql(sql)

        if planten_per_m != '':
            sql = f"""UPDATE algemeen 
                SET AANTAL_PER_M = '{planten_per_m}'
                WHERE LAT_NAAM ='{self.name_lat}' 
                """
            self.execute_sql(sql)
        
        if piet is not None:
            sql = f"""UPDATE algemeen 
                SET PIET = '{piet}'
                WHERE LAT_NAAM='{self.name_lat}' 
                """
            self.execute_sql(sql)

        if winterhard is not None:
            sql = f"""UPDATE algemeen 
                SET WINTERHARD = '{winterhard}'
                WHERE LAT_NAAM='{self.name_lat}' 
                """
            self.execute_sql(sql)
        
        if insecten is not None:
            sql = f"""UPDATE algemeen
                SET INSECTEN = '{insecten}'
                WHERE LAT_NAAM='{self.name_lat}'
                """
            self.execute_sql(sql)

        if makkelijk is not None:
            sql = f"""UPDATE algemeen
                SET MAKKELIJK = '{makkelijk}'
                WHERE LAT_NAAM='{self.name_lat}'
                """
            self.execute_sql(sql)

        if inheems is not None:
            sql = f"""UPDATE algemeen
                SET INHEEMS = '{inheems}'
                WHERE LAT_NAAM='{self.name_lat}'
                """
            self.execute_sql(sql)

        if wintergroen is not None:
            sql = f"""UPDATE algemeen
                SET WINTERGROEN = '{wintergroen}'
                WHERE LAT_NAAM='{self.name_lat}'
                """
            self.execute_sql(sql)

        if opmerkingen != '':
            sql = f"""UPDATE algemeen
                SET OPMERKINGEN = '{opmerkingen}'
                WHERE LAT_NAAM ='{self.name_lat}'
                """
            self.execute_sql(sql)

        if opmerkingen_piet != '':
            sql = f"""UPDATE algemeen
                SET OPMERKINGEN_PIET = '{opmerkingen_piet}'
                WHERE LAT_NAAM ='{self.name_lat}'
                """
            self.execute_sql(sql)

        if opmerkingen_verzorging != '':
            sql = f"""UPDATE algemeen
                SET OPMERKINGEN_VERZORGING = '{opmerkingen_verzorging}'
                WHERE LAT_NAAM ='{self.name_lat}'
                """
            self.execute_sql(sql)
        return

    def write_color(self, kleur):
        col_options = self.get_color_options()
        col_out = self.parse_options_to_bool(kleur, col_options)
        sql_columns = ', '.join(col_options)
        sql_values = [col_out[val] for val in col_options]
        sql_values = ', '.join(sql_values)
        sql = f"""INSERT INTO kleur (LAT_NAAM, {sql_columns})
            VALUES ('{self.name_lat}', {sql_values})
            """
        self.execute_sql(sql)
        return

    def write_bloom_period(self, bloeitijd):
        bloom_options = self.get_months()
        bloom_out = self.parse_options_to_bool(bloeitijd, bloom_options)
        sql_columns = ', '.join(bloom_options)
        sql_values = [bloom_out[val] for val in bloom_options]
        sql_values = ', '.join(sql_values)
        sql = f"""INSERT INTO bloeitijd (LAT_NAAM, {sql_columns})
            VALUES ('{self.name_lat}', {sql_values})
            """
        self.execute_sql(sql)
        return

    def write_structure(self, structuur):
        struc_options = self.get_structure()
        struc_out = self.parse_options_to_bool(structuur, struc_options)
        sql_columns = ', '.join(struc_options)
        sql_values = [struc_out[val] for val in struc_options]
        sql_values = ', '.join(sql_values)
        sql = f"""INSERT INTO bloeitijd (LAT_NAAM, {sql_columns})
            VALUES ('{self.name_lat}', {sql_values})
            """
        self.execute_sql(sql)
        return
         
    def write_list_booleans(self, user_values, options, table):
        db_in = self.parse_options_to_bool(user_values, options)
        sql_columns = ', '.join(options)
        sql_values = [db_in[val] for val in options]
        sql_values = ', '.join(sql_values)
        sql = f"""INSERT INTO {table} (LAT_NAAM, {sql_columns})
            VALUES ('{self.name_lat}', {sql_values})
            """
        self.execute_sql(sql)
        return

@app.route('/')
def intro():
    return render_template('intro.html')

@app.route('/niewe_plant', methods=['GET', 'POST'])
def nieuwe_plant():
    if request.method == 'POST':
        name_lat = request.form.get('lat_name')
        
        AP = AddPlant(name_lat)

        name_reg = request.form.get('regular_name')
        if name_reg != "":
            AP.write_names(name_reg)

        height = request.form.get('hoogte')
        width = request.form.get('breedte')
        AP.write_size(height, width)

        blad = request.form.get('blad')
        planten_per_m = request.form.get('planten_per_m')
        soort = request.form.get('soort')
        piet = request.form.get('piet')
        winterhard = request.form.get('winterhard')
        insecten = request.form.get('insecten')
        makkelijk = request.form.get('makkelijk')
        inheems = request.form.get('inheems')
        wintergroen = request.form.get('wintergroen')
        opmerkingen = request.form.get('opmerkingen')
        opmerkingen_piet = request.form.get('opmerkingen_piet')
        opmerkingen_verzorging = request.form.get('opmerkingen_verzorging')
        
        f = request.files['picture']
        if f.filename != '':
            _fn, fext = os.path.splitext(f.filename)
            f.save(os.path.join(PICS,  f'{name_lat}.{fext}'))


        AP.write_algemeen(blad, planten_per_m, soort, piet, winterhard, 
                          insecten, makkelijk, inheems, wintergroen, opmerkingen,
                          opmerkingen_piet, opmerkingen_verzorging)
        
        architectuur = request.form.getlist('architectuur')
        arch_opts = AP.get_arch_options()
        AP.write_list_booleans(architectuur, arch_opts, 'architectuur')

        kleur = request.form.getlist('kleur')
        col_opts = AP.get_color_options()
        AP.write_list_booleans(kleur, col_opts, 'kleur')

        bloeitijd = request.form.getlist('bloeitijd')
        months = AP.get_months()
        AP.write_list_booleans(bloeitijd, months, 'bloeitijd')

        structuur = request.form.getlist('structuur')
        struc_opts = AP.get_structure()
        AP.write_list_booleans(structuur, struc_opts, 'structuur')

        langlevend = request.form.getlist('langlevend')
        langlevend_opts = AP.get_langlevend()
        AP.write_list_booleans(langlevend, langlevend_opts, 'langlevend')

        uitbreiding = request.form.getlist('uitbreiding')
        uitbreiding_opts = AP.get_uitbreiding()
        AP.write_list_booleans(uitbreiding, uitbreiding_opts, 'uitbreiding')

        uitzaaiend = request.form.getlist('uitzaaiend')
        uitzaaiend_opts = AP.get_uitzaaiend()
        AP.write_list_booleans(uitzaaiend, uitzaaiend_opts, 'uitzaaiend')

        persistentie = request.form.getlist('persistentie')
        persistentie_opts = AP.get_persistentie()
        AP.write_list_booleans(persistentie, persistentie_opts, 'persistentie')

        vermeerderen = request.form.getlist('vermeerderen')
        vermeerderen_opts = AP.get_vermeerderen_options()
        AP.write_list_booleans(vermeerderen, vermeerderen_opts, 'vermeerderen')

        licht = request.form.getlist('licht')
        licht_opts = AP.get_licht()
        AP.write_list_booleans(licht, licht_opts, 'licht')

        grondsoort = request.form.getlist('grondsoort')
        grondsoort_opts = AP.get_grondsoort()
        AP.write_list_booleans(grondsoort, grondsoort_opts, 'grondsoort')

        del (AP)

    return render_template('nieuwe_plant.html')
