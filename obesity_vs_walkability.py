import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns

#read in data
walk_df = pd.read_csv('walkability.csv', na_values='?')
obesity_df = pd.read_csv('obesity.csv', na_values='?')

def state_hist(state):
    #filter for values for one state only
    state_df = walk_df[walk_df['STATE'] == state]
    #plot a histogram of the walkability scores for given state
    plt.figure(figsize=(10, 8))
    plt.hist(state_df['NatWalkInd'], bins=30, edgecolor='black')
    plt.title('Distribution of Walkability Scores in ' + str(state))
    plt.xlabel('Walkability Score')
    plt.ylabel('Frequency')
    plt.show()

#remove unneeded columns
walk_df = walk_df[['STATEFP','NatWalkInd','CSA_Name','CBSA_Name']]
obesity_df.drop(columns=['SHAPE_Length','SHAPE_Area'],inplace=True)
obesity_df.drop(38,inplace = True) #Remove Puerto Rico
obesity_df.reset_index(drop=True,inplace=True) # Correct indexes


#grab table from online and make dictionary of FIP codes:State 
tables = pd.read_html('https://en.wikipedia.org/wiki/Federal_Information_Processing_Standard_state_code')
state_code_dict = tables[0].set_index('Numeric code')['Name'].to_dict() #sort dict by code:state
#change values from FIP codes to state names
walk_df['STATEFP'] = walk_df['STATEFP'].map(state_code_dict)
walk_df.rename(columns={"STATEFP":"STATE"},inplace=True)

#consolidate values by state and average walkabiltiy by state
avg_walk = walk_df.groupby("STATE")["NatWalkInd"].mean().reset_index()

#cosolidate values based by state and median walkability
med_walk = walk_df.groupby("STATE")["NatWalkInd"].median().reset_index()

#rename obesity column for merging
obesity_df.rename(columns={"NAME":"STATE"},inplace=True)

#merge the dataframes
merged_df = pd.merge(obesity_df,avg_walk,on="STATE")
med_df = pd.merge(obesity_df,med_walk,on="STATE")

#set index on FID
merged_df.set_index("FID",inplace=True)
med_df.set_index("FID",inplace=True)

#rename NatWalkInd to Walkability Score
merged_df.rename(columns={"NatWalkInd":"Avg Walkability Score"},inplace=True)
med_df.rename(columns={"NatWalkInd":"Median Walkability Score"},inplace=True)

#plot average scatterplot
plt.figure(figsize=(10,8))
plt.scatter(merged_df['Avg Walkability Score'], merged_df['Obesity'])
plt.xlabel('Walkability')
plt.ylabel('Obesity Rate')
plt.title('Average Walkability Score vs Obesity Rate')
plt.show()

#plot median scatterplot
plt.figure(figsize=(10,8))
plt.scatter(med_df["Median Walkability Score"],med_df["Obesity"])
plt.xlabel('Walkability')
plt.ylabel('Obesity Rate')
plt.title('Median Walkability Score vs Obesity Rate')
plt.show()

#seaborn Avg
plt.figure(figsize=(10,8))
sns.scatterplot(data=merged_df, x='Avg Walkability Score', y='Obesity', hue='STATE')
plt.title('Avg Walkability Score vs Obesity Rate by State')
plt.show()

#seaborn Median
plt.figure(figsize=(10,8))
sns.scatterplot(data=med_df, x='Median Walkability Score', y='Obesity', hue='STATE')
plt.title('Median Walkability Score vs Obesity Rate by State')
plt.show()

#seaborn regression
plt.figure(figsize=(10,8))
sns.regplot(data=merged_df, x='Avg Walkability Score', y='Obesity')
plt.title('Regression Plot of Walkability Score vs Obesity Rate')
plt.show()

#correlation coeffecient
r = merged_df['Avg Walkability Score'].corr(merged_df['Obesity'])
print('Correlation coefficient:', r)

#load geographic information
us_states_df = gpd.read_file('cb_2018_us_state_500k.shp')
us_states_df.rename(columns={"NAME":"STATE"},inplace=True)
geo_df = us_states_df.set_index('STATE').merge(merged_df,on="STATE")

#remove Alaska
geo_df = geo_df[geo_df['STATE'] != 'Alaska']

#make heatmaps
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5))

#Obesity heatmap
geo_df.plot(column='Obesity', ax=ax1, legend=True, cmap='YlOrRd')
ax1.set_title("Obesity Heatmap")
ax1.set_xticklabels([])
ax1.set_yticklabels([])

#Avg Walkscore heatmap
geo_df.plot(column='Avg Walkability Score', ax=ax2, legend=True, cmap='RdYlBu')
ax2.set_title("Walkability Heatmap")
ax2.set_xticklabels([])
ax2.set_yticklabels([])

#display plots
plt.tight_layout()
plt.show()



#consolidate values by CSA and make value the average walkabiltiy by state
walk_df = pd.read_csv('walkability.csv')
walk_df = walk_df.groupby('CSA_Name')['NatWalkInd'].mean().reset_index()

#temp df
top_N = 20
sorted_df = walk_df.sort_values(by='NatWalkInd', ascending=True).head(top_N)
#Plot
plt.figure(figsize=(10,8))
ax = sorted_df.plot.barh(y='NatWalkInd', x='CSA_Name', legend=False)
ax.set_xlabel('Walkability Score')
ax.set_title('{} CSAs by Lowest Walkability Score'.format(top_N))

#Invert the y-axis to have the CSA with the highest score at the top
ax.invert_yaxis()

plt.tight_layout()
plt.show()
