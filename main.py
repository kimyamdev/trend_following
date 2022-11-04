from flask import Flask, render_template, request, url_for, flash, redirect
import pandas as pd
import datetime as dt
import numpy as np
import math

app = Flask(__name__)

@app.route('/')
def index():

    return render_template('index.html')

@app.route('/create', methods =["GET", "POST"])
def create():

    return render_template("create.html")


