from flask import Blueprint, render_template, request, redirect, url_for, flash
from pkg.utils import commit
from pkg.med_core import Patient, Characteristic, Drug, Treatment, MedicationRegimen, AlternativeTreatments, FollowUp
from pkg.ZODB_manager import RegistryManager

main = Blueprint('main', __name__)


@main.route('/')
def index():
    return render_template('base.html')


@main.route('/patients', methods=['GET', 'POST'])
def patients():
    if request.method == 'POST':
        try:
            population = request.form['population']
            primary_indication = request.form['primary_indication']
            size = float(request.form['size'])

            population_char = Characteristic('Population', population)
            patient = Patient(size, population)
            pi_char = Characteristic('Primary Indication', primary_indication)
            patient.add_characteristic(pi_char)

            commit(patient)
            flash('Patient added successfully!', 'success')
        
        except Exception as e:
            flash(f'Error adding patient: {e}', 'danger')
    return render_template['patient.html']


@main.route('/drug', methods=['GET', 'POST'])
def drugs():
    if request.method == 'POST':
        try:
            name = request.form['name']
            strength = request.form['strength']

            drug = Drug(name, strength)
            commit(drug)
            flash('Drug added successfully!', 'seccess')
        except Exception as e:
            flash(f'Error adding drug: {e}', 'danger')
    return render_template('drugs.html')


@main.route('/treatments', methods=['GET'])
def treatments():
    with RegistryManager() as rm:
        drugs = list(rm.get_registry('drug_registry').values())
        treatments = list(rm.get_registry('treatment_registry').values())
        noalt_treatments = [t for t in treatments if not isinstance(t, AlternativeTreatments)]
    return render_template(
        'treatments.html',
        drugs = drugs,
        noalt_treatments = noalt_treatments
        )


@main.route('/treatments/general', methods=['POST'])
def add_general_treatment():
    try:
        name = request.form['treatment_name']
        treatment = Treatment.get_or_create(name)
        commit(treatment)
        flash(f'General Treatment added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding treatment: {e}' , 'danger')
    
    return redirect(url_for('main.treatments'))


@main.routs('/treatments/regimen', methods=['POST'])
def add_medical_regimen():
    try:
        name = request.form['medical_regimen_name']
        drugs = request.form.getlist('medical_regimen_drugs')
        medication = MedicationRegimen.get_or_create(name)

        for drug_id in drugs:
            drug_name, drug_str = drug_id.split('|')
            drug = Drug(drug_name, drug_str)
            annual_patient_con = int(request.form[f'annual_con_{drug_name}'])
            medication.add_drug(drug, annual_patient_con)

        commit(medication)
        flash(f'Medication Regimen add successfully!', 'success')
    except Exception as e:
        flash(f'Error adding Medication Regimen')
    return redirect(url_for('main.treatments'))


@main.route('/treatments/alternative', methods='POST')
def add_alt_treatment():
    try:
        name = request.form('alt_name')
        selelcted_treatments = request.form.getlist('alternative_treatments')
        rates = [
            float(request.form.get(f'rate_{treatment_name}', 1.0))
            for treatment_name in selelcted_treatments
        ]

        treatments = [Treatment.get_or_create(t_name) for t_name in selelcted_treatments]
        alternative_treatment = AlternativeTreatments.get_or_create(*treatments, rates=rates)
        
        commit(alternative_treatment)
        flash('Alternative Treatment added successfully!', 'success')
    except Exception as e:
        flash(f'Error adding alternative treatment: {e}', 'danger')
    return redirect(url_for('main.treatments'))