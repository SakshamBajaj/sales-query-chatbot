# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List, Optional

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormValidationAction
from rasa_sdk.events import AllSlotsReset

import actions.get_commands as get_commands
from datetime import datetime, timedelta
#
#

class ValidateGetMetricForm(FormValidationAction):
    def name(self) -> Text:
        return "validate_get_metric_form"
        
    async def required_slots(
        self,
        slots_mapped_in_domain: List[Text],
        dispatcher: "CollectingDispatcher",
        tracker: "Tracker",
        domain: "DomainDict",
    ) -> Optional[List[Text]]:
        required_slots=["metric", "date_range", "trigger_intent"]
        intent = tracker.get_slot('trigger_intent')
        if (intent == "store_rank_by_metric") or (intent is None and tracker.latest_message['intent']['name']=='store_rank_by_metric'):
            required_slots.append("number_of_stores")
            required_slots.append("superlative")
        return required_slots

    async def extract_date_range(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        time_val = tracker.get_slot('date_range')
        time_entity = next((e for e in tracker.latest_message['entities'] if
                                    e['entity'] == 'time'), None)
        if time_entity is not None:
            print("\n \n Time entity: " + str(time_entity) + "\n \n")
            print(time_val)
            time_val = time_entity['additional_info']['values'][0]
        #    if 'holidayBeta' in time_entity['additional_info'] :
         #       time_val['to'] = time_val['to']['value']
          #      time_val['from'] = time_val['from']['value']

            if ('grain' in time_val and time_val['grain'] == 'year'):
                #Converting to financial year by changing Jan 1st to June 1st
                
                if (time_val['type']=='value'):
                    val = time_val['value']
                    time_val['value'] = val[:6] + '6' + val[7:]
                elif (time_val['type']=='interval'):
                    val = time_val['from']
                    time_val['from'] = val[:6] + '6' + val[7:]
                    val = time_val['to']
                    time_val['to'] = val[:6] + '6' + val[7:]
        else:
            time_entity = next((e for e in tracker.latest_message['entities'] if
                                    e['entity'] == 'year_extract'), None)
            print("Time Entity: " + str(time_entity))
            if time_entity is not None:
                time_val = {}
                time_val['type'] = 'value'
                time_val['grain'] = 'year'
                time_val['value'] = str(time_entity['value']) + '-06-01'
                

        return {"date_range": time_val}
    
    async def extract_number_of_stores(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        word_to_val = {
            'one': 1,
            'two': 2,
            'three': 3,
            'four': 4,
            'five': 5,
            'six': 6,
            'seven': 7,
            'eight': 8,
            'nine' : 9,
            'ten': 10,
            'eleven': 11,
            'twelve': 12,
            'thirteen': 13,
            'fourteen': 14,
            'fifteen': 15,
        }
        num_val = tracker.get_slot('number_of_stores')
        num_entity = next((e for e in tracker.latest_message['entities'] if
                                    e['entity'] == 'store_number'), None)
        print(num_val)
        print("Number Entity: " + str(num_entity))
        if num_val is None and num_entity is not None:
            try:
                num_val = int(num_entity['value'])
            except:
                num_val = word_to_val[num_entity['value']]

        return {'number_of_stores': num_val}

                            

    async def validate_number_of_stores(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        if slot_value is not None and slot_value >=1 and slot_value <= 15:
            return {"number_of_stores": slot_value}
        else:
            dispatcher.utter_message("Currently we only rank upto 15 stores.")
            return {"number_of_stores": None}
 
    #def validate_time(self, slot_value: Any, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    #) -> Dict[Text, Any]:
    #    if not isinstance(slot_value, dict):
    #        return {"time": None}
    #    else:
#            return {"time": slot_value} 


    async def extract_trigger_intent(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict
    ) -> Dict[Text, Any]:
        if tracker.get_slot('trigger_intent') is None:
            return {"trigger_intent" : tracker.latest_message['intent']['name']}
        return {"trigger_intent": tracker.get_slot('trigger_intent')}

  
    
class ActionSubmitGetMetricForm(Action):
    def name(self) -> Text:
        return "action_submit_get_metric_form"
    def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict]:
        try:
            result = 2
            metric = tracker.get_slot('metric')
            bool_budgeted = 'Budget' in metric
            start_date, end_date = get_commands.set_dates(tracker.get_slot('date_range'))

            category_filters = {'Concept': tracker.get_slot('concepts'), 
                                'Territory': tracker.get_slot('territory'),
                                'Brands': tracker.get_slot('brands'),
                            }

            store_filters = {
                'LFL / Non-LFL': tracker.get_slot('LFL_or_Non_LFL'), 
                'CP / Non-CP' : tracker.get_slot('CP_or_Non_CP'), 
                'Region': tracker.get_slot('region'),
                'Sub-Region': tracker.get_slot('sub_region'),
                'Store Type': tracker.get_slot('store_type'),
                'Store Sub-Type': tracker.get_slot('store_subtype'),
            }

            required_entities_dict = {
                'Metric': metric,
                'Calculated Metric' : tracker.get_slot('calculated_metric'),
                'Superlative': tracker.get_slot('superlative'),
                'Number Of Stores': tracker.get_slot('number_of_stores'),
                'Start Date': start_date.strftime("%a, %d %B %Y"),
                'End Date': end_date.strftime("%a, %d %B %Y"),
            }
            #start_date_string = start_date.strftime("%a, %d %B %Y")
            #end_date_string = end_date.strftime("%a, %d %B %Y")
            def format_by_key(val, key):
                if key in ['Concept', 'Brands', 'Store Type', 'Region', 'Sub-Region', 'Superlative']:
                    return val.title()
                elif key in ['Territory', 'LFL / Non-LFL', 'CP / Non-CP', 'Store Sub-Type']:
                    return val.upper()
                else:
                    return val
            def construct_filter_display_str(filter_dict):
                display_str = ""
                for key, val in filter_dict.items():
                    if val is not None:
                        if isinstance(val, list):
                            val = ', '.join(val)
                        display_str += "{key}: **{val}**\n\n".format(key=key, val=format_by_key(val, key))
                return display_str

            entity_val_str = construct_filter_display_str(required_entities_dict) + construct_filter_display_str(category_filters) + construct_filter_display_str(store_filters)

            dispatcher.utter_message(json_message={
                "type": "message",      
                "attachments": [
                        {
                        "contentType": "application/vnd.microsoft.card.adaptive",
                        "content": {
                            "type": "AdaptiveCard",
                            "version": "1.3",
                            "body": [
                            {
                                "type": "TextBlock",
                                "size": "Medium",
                                "weight": "Bolder",
                                "text": "Filters",
                            },
                            {
                                "type": "TextBlock",
                                "wrap": "true",
                                "size": "Default",
                                "text": entity_val_str,       
                            },
                            ]
                        }
                    }
                ]
           })
        

            intent = tracker.get_slot('trigger_intent')
            if intent == 'store_rank_by_metric':
                # Call rank_metric
                superlative = tracker.get_slot('superlative')
                number_of_stores = tracker.get_slot('number_of_stores')
                result = get_commands.get_stores_by_superlative_by_category_by_date_range(metric, superlative, number_of_stores, category_filters, store_filters, bool_budgeted, start_date, end_date)
                dispatcher.utter_message(
                json_message={
                    "type" : "message",
                    "attachments":[ 
                        {
                        "contentType": "application/vnd.microsoft.teams.card.o365connector",
                        "content": {
                            "@type": "MessageCard",
                            "@context": "https://schema.org/extensions",
                            "summary": "Summary",
                            "title": "Store Rankings",
                            "text" : result
                        }
                    }]
                }
                )
        
           
            elif intent == 'metric_value':
                
                if tracker.get_slot('calculated_metric') is not None:
                    calculated_metric = tracker.get_slot('calculated_metric')
                    result = get_commands.get_calculated_metric(calculated_metric, metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
                    if calculated_metric == 'PSF':
                        dispatcher.utter_message("{metric} per day per sqft is **{result}**".format(metric=metric, result=get_commands.convert_to_business(result)))
                    elif calculated_metric =='Budget Achievement':
                        dispatcher.utter_message("Budget Achievement by {metric} is **{result}%**".format(metric=metric, result=get_commands.convert_to_business(result)))
                    elif calculated_metric == 'Growth':
                        dispatcher.utter_message("The YoY growth is **{result}%**".format(result=result))

                else:   
                    result = get_commands.get_metric_for_categories_by_date_range(metric, category_filters, store_filters, bool_budgeted, start_date, end_date)
                    if get_commands.metric_type(metric) == 'value':
                        dispatcher.utter_message("{metric} is **{result}**".format(metric=metric, result=get_commands.convert_to_business(result)))
                    elif get_commands.metric_type(metric) == 'percentage':
                        dispatcher.utter_message("{metric} is **{result}%**".format(metric=metric, result=get_commands.convert_to_business(result)))
            else:
                print("Couldn't match trigger intent")
                raise Exception("Couldn't match trigger intent")
        except Exception as e:
            dispatcher.utter_message("Sorry, your request triggered an error. We will surely look into this!")
            print(e)
            #raise(e)
        return [AllSlotsReset()]