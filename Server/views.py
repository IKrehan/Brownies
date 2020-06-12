from flask import Blueprint, render_template, redirect, request, flash, url_for
from calendar import monthcalendar
from datetime import date

from .models import Agenda


views = Blueprint('views', __name__)

@views.route("/")
def Home():
    return render_template("index.html")


@views.route("/agendamento")
def Agendamento():
    return render_template("agendamento.html")
    

@views.route("/agendamento/<string:service_type>")
def Reserva(service_type):
    booked = Agenda.query.all()

    return render_template("reserva.html", booked=booked)