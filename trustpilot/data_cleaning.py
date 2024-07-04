import pandas as pd
import ast

df = pd.read_csv('trustpilot.csv')

print(len(df))

# print(df.stars.dtype)
df.info()

#drop unwanted columns
df = df.drop(['businessUnitId','identifyingName', 'logoUrl', 'isRecommendedInCategories'], axis=1)

# unpack location details
address = df['location']

def parse_dict(dict_str):
    dict_data = eval(dict_str)
    return dict_data

def parse_categories(cat_str):
    # convert string to list of dictionaries
    try:
        categories_list = ast.literal_eval(cat_str)
        return categories_list
    except ValueError:
        return []
    
def extract_agency(category_list):
    # Function to extract agency_type from categories_list
    return ','.join(cat['displayName'] for cat in category_list)


# location details
df['location_details'] = df['location'].apply(parse_dict)
df['address'] = df['location_details'].apply(lambda x: x['address'])
df['city'] = df['location_details'].apply(lambda x: x['city'])
df['zipcode'] = df['location_details'].apply(lambda x: x['zipCode'])
df['country'] = df['location_details'].apply(lambda x: x['country'])

#contact details
df['contact_details'] = df['contact'].apply(parse_dict)
df['website'] = df['contact_details'].apply(lambda x: x['website'])
df['email'] = df['contact_details'].apply(lambda x: x['email'])
df['phone'] = df['contact_details'].apply(lambda x: x['phone'])


# categories
# Apply the function to parse the categories column
df['categories_list'] = df['categories'].apply(parse_categories)

# extract agency type from categories_list
df['agency_type'] = df['categories_list'].apply(extract_agency)
df.drop(['categories_list', 'contact_details', 'location_details'], inplace=True, axis=1)
df.drop(['location', 'contact', 'categories'], axis=1, inplace=True)
df.to_csv('cleaned_data.csv')