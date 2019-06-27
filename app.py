{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "metadata": {},
   "outputs": [],
   "source": [
    "%matplotlib inline\n",
    "from matplotlib import style\n",
    "style.use('fivethirtyeight')\n",
    "import matplotlib.pyplot as plt\n",
    "import numpy as np\n",
    "import pandas as pd\n",
    "import datetime as dt\n",
    "import sqlalchemy\n",
    "from sqlalchemy.ext.automap import automap_base\n",
    "from sqlalchemy.orm import Session\n",
    "from sqlalchemy import create_engine, func, inspect\n",
    "from flask import Flask, jsonify"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Reflect Tables into SQLAlchemy ORM"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "metadata": {},
   "outputs": [],
   "source": [
    "engine = create_engine(\"sqlite:///Resources/hawaii.sqlite\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 3,
   "metadata": {},
   "outputs": [],
   "source": [
    "# reflect an existing database into a new model\n",
    "Base = automap_base()\n",
    "# reflect the tables\n",
    "Base.prepare(engine, reflect=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 4,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "['measurement', 'station']"
      ]
     },
     "execution_count": 4,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# We can view all of the classes that automap found\n",
    "Base.classes.keys()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 5,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Save references to each table\n",
    "Measurement = Base.classes.measurement\n",
    "Station = Base.classes.station"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 6,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create our session (link) from Python to the DB\n",
    "session = Session(engine)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 7,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "measurement\n",
      "id INTEGER\n",
      "station TEXT\n",
      "date TEXT\n",
      "prcp FLOAT\n",
      "tobs FLOAT\n",
      " \n",
      "station\n",
      "id INTEGER\n",
      "station TEXT\n",
      "name TEXT\n",
      "latitude FLOAT\n",
      "longitude FLOAT\n",
      "elevation FLOAT\n"
     ]
    }
   ],
   "source": [
    "#Use inspector to get column data\n",
    "inspector = inspect(engine)\n",
    "inspector.get_table_names()\n",
    "print('measurement')\n",
    "columns = inspector.get_columns('measurement')\n",
    "for column in columns:\n",
    "    print(column[\"name\"], column[\"type\"])\n",
    "\n",
    "print(\" \")    \n",
    "print(\"station\")\n",
    "columns = inspector.get_columns('station')\n",
    "for column in columns:\n",
    "    print(column[\"name\"], column[\"type\"])"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "# Exploratory Climate Analysis"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 8,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "('2017-08-23')"
      ]
     },
     "execution_count": 8,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Calculate the date 1 year ago from the last data point in the database\n",
    "session.query(Measurement.date).order_by(Measurement.date.desc()).first()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 9,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<matplotlib.axes._subplots.AxesSubplot at 0x20766b0b080>"
      ]
     },
     "execution_count": 9,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "# Design a query to retrieve the last 12 months of precipitation data and plot the results\n",
    "# Perform a query to retrieve the data and precipitation scores\n",
    "\n",
    "last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()\n",
    "#Would just use dt to find today and subtract 365 days if there was data available\n",
    "yearback = dt.date(2017,8,23) - dt.timedelta(days = 365)\n",
    "precip_data = session.query(Measurement.prcp, Measurement.date).filter(Measurement.date >= f'{yearback}')\n",
    "# Save the query results as a Pandas DataFrame and set the index to the date column\n",
    "# Sort the dataframe by date\n",
    "\n",
    "precip_data_df = pd.DataFrame(precip_data)\n",
    "precip_data_sorted = precip_data_df.sort_values(by='date')\n",
    "precip_data_sorted = precip_data_sorted.set_index('date')\n",
    "precip_data_sorted.columns = ['precipitation']\n",
    "# Use Pandas Plotting with Matplotlib to plot the data\n",
    "\n",
    "precip_data_sorted.plot(xticks=[])\n",
    "\n",
    "# Calculate the date 1 year ago from the last data point in the database"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 10,
   "metadata": {},
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>prcp</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>count</th>\n",
       "      <td>2021.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>mean</th>\n",
       "      <td>0.177279</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>std</th>\n",
       "      <td>0.461190</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>min</th>\n",
       "      <td>0.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>25%</th>\n",
       "      <td>0.000000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>50%</th>\n",
       "      <td>0.020000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>75%</th>\n",
       "      <td>0.130000</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>max</th>\n",
       "      <td>6.700000</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "              prcp\n",
       "count  2021.000000\n",
       "mean      0.177279\n",
       "std       0.461190\n",
       "min       0.000000\n",
       "25%       0.000000\n",
       "50%       0.020000\n",
       "75%       0.130000\n",
       "max       6.700000"
      ]
     },
     "execution_count": 10,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# Use Pandas to calcualte the summary statistics for the precipitation data\n",
    "precip_data_df.describe()"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 11,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " There are 9 stations which reported data during this time\n"
     ]
    }
   ],
   "source": [
    "# Design a query to show how many stations are available in this dataset?\n",
    "M_Stations = session.query(Measurement.station).group_by(Measurement.station).count()\n",
    "print(f' There are {M_Stations} stations which reported data during this time')"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 12,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "data": {
      "text/html": [
       "<div>\n",
       "<style scoped>\n",
       "    .dataframe tbody tr th:only-of-type {\n",
       "        vertical-align: middle;\n",
       "    }\n",
       "\n",
       "    .dataframe tbody tr th {\n",
       "        vertical-align: top;\n",
       "    }\n",
       "\n",
       "    .dataframe thead th {\n",
       "        text-align: right;\n",
       "    }\n",
       "</style>\n",
       "<table border=\"1\" class=\"dataframe\">\n",
       "  <thead>\n",
       "    <tr style=\"text-align: right;\">\n",
       "      <th></th>\n",
       "      <th>station</th>\n",
       "      <th>count</th>\n",
       "    </tr>\n",
       "  </thead>\n",
       "  <tbody>\n",
       "    <tr>\n",
       "      <th>0</th>\n",
       "      <td>USC00519281</td>\n",
       "      <td>2772</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>1</th>\n",
       "      <td>USC00519397</td>\n",
       "      <td>2724</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>2</th>\n",
       "      <td>USC00513117</td>\n",
       "      <td>2709</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>3</th>\n",
       "      <td>USC00519523</td>\n",
       "      <td>2669</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>4</th>\n",
       "      <td>USC00516128</td>\n",
       "      <td>2612</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>5</th>\n",
       "      <td>USC00514830</td>\n",
       "      <td>2202</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>6</th>\n",
       "      <td>USC00511918</td>\n",
       "      <td>1979</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>7</th>\n",
       "      <td>USC00517948</td>\n",
       "      <td>1372</td>\n",
       "    </tr>\n",
       "    <tr>\n",
       "      <th>8</th>\n",
       "      <td>USC00518838</td>\n",
       "      <td>511</td>\n",
       "    </tr>\n",
       "  </tbody>\n",
       "</table>\n",
       "</div>"
      ],
      "text/plain": [
       "       station  count\n",
       "0  USC00519281   2772\n",
       "1  USC00519397   2724\n",
       "2  USC00513117   2709\n",
       "3  USC00519523   2669\n",
       "4  USC00516128   2612\n",
       "5  USC00514830   2202\n",
       "6  USC00511918   1979\n",
       "7  USC00517948   1372\n",
       "8  USC00518838    511"
      ]
     },
     "execution_count": 12,
     "metadata": {},
     "output_type": "execute_result"
    }
   ],
   "source": [
    "# What are the most active stations? (i.e. what stations have the most rows)?\n",
    "\n",
    "station_list = []\n",
    "station_count = []\n",
    "\n",
    "# List the stations and the counts in descending order.\n",
    "Stations_C = session.query(Measurement.station).group_by(Measurement.station).all()\n",
    "\n",
    "#Create list of stations\n",
    "for stations in Stations_C:\n",
    "    station_list.append(stations)\n",
    "    \n",
    "#Convert list of tuples to list of strings\n",
    "station_list = [i[0] for i in station_list]\n",
    "station_list\n",
    "\n",
    "#get reading count for each station\n",
    "for stations in station_list:\n",
    "    station_counts = session.query(Measurement.station).filter(Measurement.station == f'{stations}')\n",
    "    station_count.append(station_counts.count())\n",
    "    \n",
    "#combine data into a df and sort largest to smallest\n",
    "station_dict = {'station':station_list}\n",
    "count_dict = {'count':station_count}\n",
    "station_count_df = pd.DataFrame(station_dict)\n",
    "station_count_df['count'] = station_count\n",
    "station_count_df = station_count_df.sort_values(by = 'count', ascending=False)\n",
    "station_count_df = station_count_df.reset_index(drop=True)\n",
    "station_count_df"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 13,
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      " The maximum Temperature reported from station USC00519281 is 85F\n",
      " The minimum Temperature reported from station USC00519281 is 54F\n",
      " The average Temperature reported from station USC00519281 is 72F\n"
     ]
    }
   ],
   "source": [
    "# Using the station id from the previous query, calculate the lowest temperature recorded, \n",
    "# highest temperature recorded, and average temperature most active station?\n",
    "temp_data =session.query(Measurement.tobs).filter(Measurement.station == station_count_df['station'][0]).all()\n",
    "temp_data = [i[0] for i in temp_data]\n",
    "print(f\" The maximum Temperature reported from station {station_count_df['station'][0]} is {round(max(temp_data))}F\")\n",
    "print(f\" The minimum Temperature reported from station {station_count_df['station'][0]} is {round(min(temp_data))}F\")\n",
    "print(f\" The average Temperature reported from station {station_count_df['station'][0]} is {round(sum(temp_data)/len(temp_data))}F\")\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 14,
   "metadata": {
    "scrolled": true
   },
   "outputs": [
    {
     "data": {
      "text/plain": [
       "<matplotlib.legend.Legend at 0x2076b4cf320>"
      ]
     },
     "execution_count": 14,
     "metadata": {},
     "output_type": "execute_result"
    },
    {
     "data": {
      "image/png": "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\n",
      "text/plain": [
       "<Figure size 432x288 with 1 Axes>"
      ]
     },
     "metadata": {
      "needs_background": "light"
     },
     "output_type": "display_data"
    }
   ],
   "source": [
    "# Choose the station with the highest number of temperature observations.\n",
    "# Query the last 12 months of temperature observation data for this station and plot the results as a histogram\n",
    "\n",
    "hist_data = (session.query(Measurement.tobs).filter(Measurement.station == station_count_df['station'][0]).filter(Measurement.date > yearback).all())\n",
    "\n",
    "\n",
    "n, bins, patches = plt.hist(hist_data, bins=12, density=False, facecolor='dodgerblue', alpha=1, histtype='barstacked')\n",
    "\n",
    "plt.xlim(55,85)\n",
    "plt.ylabel('Frequency')\n",
    "plt.xlabel('Temp(F)')\n",
    "plt.xticks([60,65,70,75,80])\n",
    "plt.legend(['tobs'])"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 15,
   "metadata": {},
   "outputs": [],
   "source": [
    "#Create Dict for Flask precip\n",
    "precip_data_df = precip_data_df.set_index('date')\n",
    "precip_data_dict = precip_data_df.to_dict"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 16,
   "metadata": {},
   "outputs": [],
   "source": [
    "#create query for Flask tobs\n",
    "flask_tobs_data = (session.query(Measurement.tobs,Measurement.date,Measurement.station).filter(Measurement.station == station_count_df['station'][0]).filter(Measurement.date > yearback).all())\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 18,
   "metadata": {},
   "outputs": [],
   "source": [
    "##Flask App\n",
    "\n",
    "#Create app\n",
    "app = Flask(__name__)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 23,
   "metadata": {},
   "outputs": [
    {
     "ename": "AssertionError",
     "evalue": "View function mapping is overwriting an existing endpoint function: home",
     "output_type": "error",
     "traceback": [
      "\u001b[1;31m---------------------------------------------------------------------------\u001b[0m",
      "\u001b[1;31mAssertionError\u001b[0m                            Traceback (most recent call last)",
      "\u001b[1;32m<ipython-input-23-ccd196e6d219>\u001b[0m in \u001b[0;36m<module>\u001b[1;34m\u001b[0m\n\u001b[0;32m      1\u001b[0m \u001b[1;31m#define index\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m----> 2\u001b[1;33m \u001b[1;33m@\u001b[0m\u001b[0mapp\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mroute\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m'/'\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m      3\u001b[0m \u001b[1;32mdef\u001b[0m \u001b[0mhome\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m      4\u001b[0m     \u001b[0mprint\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m'Server recieved request for Home'\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m      5\u001b[0m     return( f\"Welcome to the Example Climate API<br\\>\"\n",
      "\u001b[1;32m~\\anaconda\\Anaconda3\\lib\\site-packages\\flask\\app.py\u001b[0m in \u001b[0;36mdecorator\u001b[1;34m(f)\u001b[0m\n\u001b[0;32m   1248\u001b[0m         \u001b[1;32mdef\u001b[0m \u001b[0mdecorator\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mf\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m   1249\u001b[0m             \u001b[0mendpoint\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0moptions\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mpop\u001b[0m\u001b[1;33m(\u001b[0m\u001b[1;34m'endpoint'\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;32mNone\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[1;32m-> 1250\u001b[1;33m             \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0madd_url_rule\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mrule\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mendpoint\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mf\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;33m**\u001b[0m\u001b[0moptions\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m   1251\u001b[0m             \u001b[1;32mreturn\u001b[0m \u001b[0mf\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m   1252\u001b[0m         \u001b[1;32mreturn\u001b[0m \u001b[0mdecorator\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32m~\\anaconda\\Anaconda3\\lib\\site-packages\\flask\\app.py\u001b[0m in \u001b[0;36mwrapper_func\u001b[1;34m(self, *args, **kwargs)\u001b[0m\n\u001b[0;32m     64\u001b[0m                 \u001b[1;34m'database models and everything related at a central place '\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m     65\u001b[0m                 'before the application starts serving requests.')\n\u001b[1;32m---> 66\u001b[1;33m         \u001b[1;32mreturn\u001b[0m \u001b[0mf\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mself\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;33m*\u001b[0m\u001b[0margs\u001b[0m\u001b[1;33m,\u001b[0m \u001b[1;33m**\u001b[0m\u001b[0mkwargs\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0m\u001b[0;32m     67\u001b[0m     \u001b[1;32mreturn\u001b[0m \u001b[0mupdate_wrapper\u001b[0m\u001b[1;33m(\u001b[0m\u001b[0mwrapper_func\u001b[0m\u001b[1;33m,\u001b[0m \u001b[0mf\u001b[0m\u001b[1;33m)\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m     68\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;32m~\\anaconda\\Anaconda3\\lib\\site-packages\\flask\\app.py\u001b[0m in \u001b[0;36madd_url_rule\u001b[1;34m(self, rule, endpoint, view_func, provide_automatic_options, **options)\u001b[0m\n\u001b[0;32m   1219\u001b[0m             \u001b[1;32mif\u001b[0m \u001b[0mold_func\u001b[0m \u001b[1;32mis\u001b[0m \u001b[1;32mnot\u001b[0m \u001b[1;32mNone\u001b[0m \u001b[1;32mand\u001b[0m \u001b[0mold_func\u001b[0m \u001b[1;33m!=\u001b[0m \u001b[0mview_func\u001b[0m\u001b[1;33m:\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m   1220\u001b[0m                 raise AssertionError('View function mapping is overwriting an '\n\u001b[1;32m-> 1221\u001b[1;33m                                      'existing endpoint function: %s' % endpoint)\n\u001b[0m\u001b[0;32m   1222\u001b[0m             \u001b[0mself\u001b[0m\u001b[1;33m.\u001b[0m\u001b[0mview_functions\u001b[0m\u001b[1;33m[\u001b[0m\u001b[0mendpoint\u001b[0m\u001b[1;33m]\u001b[0m \u001b[1;33m=\u001b[0m \u001b[0mview_func\u001b[0m\u001b[1;33m\u001b[0m\u001b[1;33m\u001b[0m\u001b[0m\n\u001b[0;32m   1223\u001b[0m \u001b[1;33m\u001b[0m\u001b[0m\n",
      "\u001b[1;31mAssertionError\u001b[0m: View function mapping is overwriting an existing endpoint function: home"
     ]
    }
   ],
   "source": [
    "#define index\n",
    "@app.route('/')\n",
    "def home():\n",
    "    print('Server recieved request for Home')\n",
    "    return( f\"Welcome to the Example Climate API<br\\>\"\n",
    "            f\"Available Routes:<br>\"\n",
    "            f\"/api/v1.0/precipitation<br>\"\n",
    "            f\"/api/v1.0/stations<br>\"\n",
    "            f\"/api/v1.0/tobs<br>\"\n",
    "            f\"/api/v1.0/<start>\"\n",
    "          )\n",
    "@app.route('/api/v1.0/precipitation')\n",
    "def precip():\n",
    "    print('Server recieved request for Temperature')\n",
    "    return(jsonify(precip_data_dict))\n",
    "    \n",
    "@app.route('/api/v1.0/stations')\n",
    "def r_stations():\n",
    "    print('Server recieved request for Sations')\n",
    "    return(jsonify(station_dict))\n",
    "\n",
    "@app.route('/api/v1.0/tobs')\n",
    "def tops():\n",
    "    print('Server recieved request for Tobs Ovservations')\n",
    "    return(jsonify(flask_tobs_data)\n",
    "          )\n",
    "\n",
    "        \n",
    "if __name__ == \"__main__\":\n",
    "    app.run(debug=True)"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# This function called `calc_temps` will accept start date and end date in the format '%Y-%m-%d' \n",
    "# and return the minimum, average, and maximum temperatures for that range of dates\n",
    "def calc_temps(start_date, end_date):\n",
    "    \"\"\"TMIN, TAVG, and TMAX for a list of dates.\n",
    "    \n",
    "    Args:\n",
    "        start_date (string): A date string in the format %Y-%m-%d\n",
    "        end_date (string): A date string in the format %Y-%m-%d\n",
    "        \n",
    "    Returns:\n",
    "        TMIN, TAVE, and TMAX\n",
    "    \"\"\"\n",
    "    \n",
    "    return session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\\\n",
    "        filter(Measurement.date >= start_date).filter(Measurement.date <= end_date).all()\n",
    "\n",
    "# function usage example\n",
    "print(calc_temps('2012-02-28', '2012-03-05'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Use your previous function `calc_temps` to calculate the tmin, tavg, and tmax \n",
    "# for your trip using the previous year's data for those same dates.\n",
    "print(calc_temps('2017-08-19','2017-08-23'))"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Plot the results from your previous query as a bar chart. \n",
    "# Use \"Trip Avg Temp\" as your Title\n",
    "# Use the average temperature for the y value\n",
    "# Use the peak-to-peak (tmax-tmin) value as the y error bar (yerr)\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Calculate the total amount of rainfall per weather station for your trip dates using the previous year's matching dates.\n",
    "# Sort this in descending order by precipitation amount and list the station, name, latitude, longitude, and elevation\n",
    "\n"
   ]
  },
  {
   "cell_type": "markdown",
   "metadata": {},
   "source": [
    "## Optional Challenge Assignment"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Create a query that will calculate the daily normals \n",
    "# (i.e. the averages for tmin, tmax, and tavg for all historic data matching a specific month and day)\n",
    "\n",
    "def daily_normals(date):\n",
    "    \"\"\"Daily Normals.\n",
    "    \n",
    "    Args:\n",
    "        date (str): A date string in the format '%m-%d'\n",
    "        \n",
    "    Returns:\n",
    "        A list of tuples containing the daily normals, tmin, tavg, and tmax\n",
    "    \n",
    "    \"\"\"\n",
    "    \n",
    "    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]\n",
    "    return session.query(*sel).filter(func.strftime(\"%m-%d\", Measurement.date) == date).all()\n",
    "    \n",
    "daily_normals(\"01-01\")"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# calculate the daily normals for your trip\n",
    "# push each tuple of calculations into a list called `normals`\n",
    "\n",
    "# Set the start and end date of the trip\n",
    "\n",
    "# Use the start and end date to create a range of dates\n",
    "\n",
    "# Stip off the year and save a list of %m-%d strings\n",
    "\n",
    "# Loop through the list of %m-%d strings and calculate the normals for each date\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Load the previous query results into a Pandas DataFrame and add the `trip_dates` range as the `date` index\n"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "metadata": {},
   "outputs": [],
   "source": [
    "# Plot the daily normals as an area plot with `stacked=False`\n"
   ]
  }
 ],
 "metadata": {
  "kernel_info": {
   "name": "python3"
  },
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.7.3"
  },
  "nteract": {
   "version": "0.12.3"
  },
  "varInspector": {
   "cols": {
    "lenName": 16,
    "lenType": 16,
    "lenVar": 40
   },
   "kernels_config": {
    "python": {
     "delete_cmd_postfix": "",
     "delete_cmd_prefix": "del ",
     "library": "var_list.py",
     "varRefreshCmd": "print(var_dic_list())"
    },
    "r": {
     "delete_cmd_postfix": ") ",
     "delete_cmd_prefix": "rm(",
     "library": "var_list.r",
     "varRefreshCmd": "cat(var_dic_list()) "
    }
   },
   "types_to_exclude": [
    "module",
    "function",
    "builtin_function_or_method",
    "instance",
    "_Feature"
   ],
   "window_display": false
  }
 },
 "nbformat": 4,
 "nbformat_minor": 2
}
