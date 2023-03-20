# -*- coding: utf-8 -*-
"""Simple fact sample app."""

import random
import logging
import json
import prompts
import openai
import os
#from langchain.llms import OpenAI

api_key_string = os.environ['OPENAI_API_KEY']
openai.api_key = api_key_string

def set_open_params(
    model="text-davinci-003",
    temperature=0.7,
    max_tokens=256,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0,
):
    """ set openai parameters"""

    openai_params = {}    

    openai_params['model'] = model
    openai_params['temperature'] = temperature
    openai_params['max_tokens'] = max_tokens
    openai_params['top_p'] = top_p
    openai_params['frequency_penalty'] = frequency_penalty
    openai_params['presence_penalty'] = presence_penalty
    return openai_params

def get_completion(params, prompt):
    """ GET completion from openai api"""
    response = openai.Completion.create(
        engine = params['model'],
        prompt = prompt,
        temperature = params['temperature'],
        max_tokens = params['max_tokens'],
        top_p = params['top_p'],
        frequency_penalty = params['frequency_penalty'],
        presence_penalty = params['presence_penalty'],
    )
    return response

def run_prompt(prompt, temperature=0.7):
    """ run prompt """
    params = set_open_params(temperature=temperature)
    response = get_completion(params, prompt)
    # print(f'\nPROMPT: {prompt}')
    print(f'RESPONSE: {response.choices[0].text}')
    return response.choices[0].text

def get_response(prompt):
    #prompt = """When I was 6 my sister was half my age. Now
    #I’m 70, how old is my sister?"""
    return run_prompt(prompt, 0.7)

from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import (
    AbstractRequestHandler, AbstractExceptionHandler,
    AbstractRequestInterceptor, AbstractResponseInterceptor)
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model.ui import SimpleCard
from ask_sdk_model import Response

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


# Built-in Intent Handlers
class DefaultHandler(AbstractRequestHandler):
    """Handler for Skill Launch and Default Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_request_type("LaunchRequest")(handler_input) or
                is_intent_name("ROLL")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In DefaultHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        #roll_result = random.randrange(1, 20000)
        
        response = get_response(prompt)
        #speech = data[prompts.GET_MESSAGE].format(roll_result)
        speech = response

        handler_input.response_builder.speak(speech).set_card(
            SimpleCard(data[prompts.SKILL_NAME], roll_result))
        return handler_input.response_builder.response


class HelpIntentHandler(AbstractRequestHandler):
    """Handler for Help Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.HelpIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In HelpIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.HELP_MESSAGE]
        reprompt = data[prompts.HELP_REPROMPT]
        handler_input.response_builder.speak(speech).ask(
            reprompt).set_card(SimpleCard(
                data[prompts.SKILL_NAME], speech))
        return handler_input.response_builder.response


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return (is_intent_name("AMAZON.CancelIntent")(handler_input) or
                is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In CancelOrStopIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.STOP_MESSAGE]
        handler_input.response_builder.speak(speech)
        return handler_input.response_builder.response


class FallbackIntentHandler(AbstractRequestHandler):
    """Handler for Fallback Intent.

    AMAZON.FallbackIntent is only available in en-US locale.
    This handler will not be triggered except in that locale,
    so it is safe to deploy on any locale.
    """

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_intent_name("AMAZON.FallbackIntent")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In FallbackIntentHandler")

        # get localization data
        data = handler_input.attributes_manager.request_attributes["_"]

        speech = data[prompts.FALLBACK_MESSAGE]
        reprompt = data[prompts.FALLBACK_REPROMPT]
        handler_input.response_builder.speak(speech).ask(
            reprompt)
        return handler_input.response_builder.response


class LocalizationInterceptor(AbstractRequestInterceptor):
    """
    Add function to request attributes, that can load locale specific data.
    """

    def process(self, handler_input):
        locale = handler_input.request_envelope.request.locale
        logger.info("Locale is {}".format(locale[:2]))

        # localized strings stored in language_strings.json
        with open("language_strings.json") as language_prompts:
            language_data = json.load(language_prompts)
        # set default translation data to broader translation
        data = language_data[locale[:2]]
        # if a more specialized translation exists, then select it instead
        # example: "fr-CA" will pick "fr" translations first, but if "fr-CA" translation exists,
        #          then pick that instead
        if locale in language_data:
            data.update(language_data[locale])
        handler_input.attributes_manager.request_attributes["_"] = data


class SessionEndedRequestHandler(AbstractRequestHandler):
    """Handler for Session End."""

    def can_handle(self, handler_input):
        # type: (HandlerInput) -> bool
        return is_request_type("SessionEndedRequest")(handler_input)

    def handle(self, handler_input):
        # type: (HandlerInput) -> Response
        logger.info("In SessionEndedRequestHandler")

        logger.info("Session ended reason: {}".format(
            handler_input.request_envelope.request.reason))
        return handler_input.response_builder.response


# Exception Handler
class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Catch all exception handler, log exception and
    respond with custom message.
    """

    def can_handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> bool
        return True

    def handle(self, handler_input, exception):
        # type: (HandlerInput, Exception) -> Response
        logger.info("In CatchAllExceptionHandler")
        logger.error(exception, exc_info=True)

        handler_input.response_builder.speak(EXCEPTION_MESSAGE).ask(HELP_REPROMPT)

        return handler_input.response_builder.response


# Request and Response loggers
class RequestLogger(AbstractRequestInterceptor):
    """Log the alexa requests."""

    def process(self, handler_input):
        # type: (HandlerInput) -> None
        logger.debug("Alexa Request: {}".format(
            handler_input.request_envelope.request))


class ResponseLogger(AbstractResponseInterceptor):
    """Log the alexa responses."""

    def process(self, handler_input, response):
        # type: (HandlerInput, Response) -> None
        logger.debug("Alexa Response: {}".format(response))


# Register intent handlers
sb.add_request_handler(DefaultHandler())
sb.add_request_handler(HelpIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_request_handler(FallbackIntentHandler())
sb.add_request_handler(SessionEndedRequestHandler())

# Register exception handlers
sb.add_exception_handler(CatchAllExceptionHandler())

# Register request and response interceptors
sb.add_global_request_interceptor(LocalizationInterceptor())
sb.add_global_request_interceptor(RequestLogger())
sb.add_global_response_interceptor(ResponseLogger())

# Handler name that is used on AWS lambda
#lambda_handler = sb.lambda_handler()


import json

def lambda_handler(event, context):
    # Retrieve the intent name from the Alexa request
    #intent_name = event['request']['intent']['name']
    intent_name = "default"
    event_json = json.dumps(event)
    print(event_json)
    if event['request']['type'] == 'LaunchRequest':
        response = {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': 'Hit me:'
                },
                'shouldEndSession': False
            }
        }

    elif 'intent' in event['request'] and 'name' in event['request']['intent'] and event['request']['intent']['name'] == 'SearchIntent':
        query_value = event['request']['intent']['slots']['Query']['value']
        response_speech = get_response(query_value)
        response = {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': response_speech
                },
                'shouldEndSession': True
            }
        }
    
    # If the user has not yet provided their name, ask for it
    # if intent_name == 'AskNameIntent':
    #     # Respond with the ask-for-name prompt
    elif 'intent' in event['request'] and 'name' in event['request']['intent'] and event['request']['intent']['name'] == 'AMAZON.FallbackIntent':
        # Retrieve the name provided by the user
        #name = event['request']['intent']['slots']['Name']['value']
        
        # Respond with the hello prompt, including the user's name
        response = {
            'version': '1.0',
            'response': {
                'outputSpeech': {
                    'type': 'PlainText',
                    'text': f'Welcome to Fallback intent!'
                },
                'shouldEndSession': True
            }
        }

    
    # If the user has provided their name, say hello
    return response
