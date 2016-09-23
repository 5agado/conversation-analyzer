import json
from watson_developer_cloud import ToneAnalyzerV3

def getToneAnalyzerService(username, password):
    toneAnalyzer = ToneAnalyzerV3(
        username=username,
        password=password,
        version=ToneAnalyzerV3.latest_version,
        x_watson_learning_opt_out=True)
    return toneAnalyzer

def extractToneFrom(text, toneService):
    res = toneService.tone(text, tones='emotion')
    tones = res['document_tone']['tone_categories'][0]['tones']
    tones = dict([(t['tone_id'], t['score']) for t in tones])
    return tones