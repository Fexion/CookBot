from flask import render_template
from ufal.udpipe import Model, Pipeline
from conllu import parse
import requests
from food_funcs import *

model = Model.load("english-partut-ud-2.0-170801.udpipe")
pipeline = Pipeline(model, 'generic_tokenizer', '', '', '')

num_dict = {'first': 1, 'second': 2, 'third': 3,
            'fourth': 4, 'fifth': 5, 'sixth': 6, 'seventh': 7,
            'eighth': 8, 'ninth': 9, 'tenth': 10, 'last': 10,
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10}


def use_udpipe(text):
    parsed = pipeline.process(text)
    return parse(parsed)


class Dialog():
    state = 0
    state_info = []
    recipe_num = 0
    offset = 0
    search_type = ''
    ingrs = []
    dishes = []
    current_step = 0
    recipes = []
    key = 'b390bba8e2msh992b9fb4f5c97e1p1118b0jsnf8047683d67d'
    google_api_key = "AIzaSyDLTUknb2JXZiiWsl_hnnrTxUfz7UHdaOM"
    headers = {
        'X-Mashape-Key': key,
        'X-Mashape-Host': 'spoonacular-recipe-food-nutrition-v1.p.mashape.com'
    }

    def process_dialog(self, text):
        switch = [
            self._state_0,
            self._state_1,
            self._state_2,
            self._state_3,
        ]
        return switch[self.state](text)

    def _reset(self):
        self.state = 0
        self.state_info = []
        self.recipe_num = 0
        self.offset = 0
        self.search_type = ''
        self.ingrs = []
        self.dishes = []
        self.current_step = 0
        self.recipes = []

    def _state_0(self, text):
        detected_food = detect_food_request(text, self.key).json()
        self.dishes, self.ingrs = [], []
        anns_list = detected_food["annotations"]

        for i in range(len(anns_list)):
            if anns_list[i]["tag"] == 'dish':
                self.dishes.append(anns_list[i]['annotation'])
            else:
                self.ingrs.append(anns_list[i]['annotation'])

        if len(self.dishes) == len(self.ingrs) == 0:
            flag_0 = text.lower().find('random')
            flag_1 = text.lower().find('something')
            if flag_0 == -1 and flag_1 == -1:
                return 'Please, repeat your query'


        if self.dishes:
            dish = self.dishes[0]
        else:
            dish = []
        self.recipes = search_recipe(dish,
                                     self.ingrs,
                                     self.key).json()['results']
        self.state = 1
        self.offset = 0
        return render_template('list_template.html',
                               recipe_list=self.recipes[self.offset*10: (self.offset+1)*10],
                               enumerate=enumerate)

    def _state_1(self, text):
        self.recipe_num = 0
        num = self._show_num(text)
        if num != -1:
            num -= 1
            if num > 10 or num == -1 or num+self.offset*10 >= len(self.recipes):
                return 'Please, repeat your query, wrong number'
            self.state = 2
            self.current_num = num

            return render_template('details_template.html',
                                   recipe=self.recipes[self.current_num + self.offset * 10])

        if self._detect_more(text):
            self.offset += 1
            if self.offset == int((len(self.recipes) - 1)/10) + 1:
                self.offset -= 1
                return 'No more recipes'

            return render_template('list_template.html',
                                   recipe_list=self.recipes[self.offset*10: (self.offset+1)*10],
                                   enumerate=enumerate)

        if self._detect_previous(text):
            self.offset -= 1
            if self.offset < 0:
                self.offset = 0
                return 'This is the first list of recipes'
            return render_template('list_template.html',
                                   recipe_list=self.recipes[self.offset*10: (self.offset+1)*10],
                                   enumerate=enumerate)

        if self._detect_exit(text):
            self._reset()
            return 'Waiting for query'

        return self._state_0(text)

    def _state_2(self, text):
        if self._detect_exit(text):
            self._reset()
            return 'Waiting for query'

        if self._detect_video(text):
            link = get_video_link(self.recipes[self.current_num + self.offset * 10]['title'],
                                  self.google_api_key)
            return render_template('youtube_template.html', yt_link=link)

        if self._detect_list(text):
            self.current_num = 0
            self.state = 1
            return render_template('list_template.html',
                               recipe_list=self.recipes[self.offset*10: (self.offset+1)*10],
                               enumerate=enumerate)

        if self._detect_start(text):
            self.state = 3
            self.current_step = 0
            step = self.recipes[self.offset*10+self.current_num]['analyzedInstructions'][0]['steps'][self.current_step]
            return render_template('step_template.html', step=step)

        num = self._show_num(text)
        if num != -1:
            num -= 1
            if num > 10 or num == -1 or num+self.offset*10 >= len(self.recipes):
                return 'Please, repeat your query, wrong number'
            self.state = 2
            self.current_num = num
            return render_template('details_template.html',
                                   recipe=self.recipes[self.current_num + self.offset * 10])

        return self._state_0(text)

    def _state_3(self, text):
        if self._detect_details(text):
            self.state = 2
            self.current_step = 0
            return render_template('details_template.html',
                                   recipe=self.recipes[self.current_num + self.offset * 10])

        if self._detect_previous(text):
            if self.current_step == 0:
                return 'This is the first step'
            self.current_step -= 1
            step = self.recipes[self.offset*10+self.current_num]['analyzedInstructions'][0]['steps'][self.current_step]
            return render_template('step_template.html', step=step)

        if self._detect_next(text):
            if self.current_step == len(self.recipes[self.offset*10+self.current_num]['analyzedInstructions'][0]['steps']) - 1:
                return 'This is final step.\n Congrats, now you have something to eat!'
            self.current_step += 1
            step = self.recipes[self.offset*10+self.current_num]['analyzedInstructions'][0]['steps'][self.current_step]
            return render_template('step_template.html', step=step)

        if self._detect_exit(text):
            self._reset()
            return 'Waiting for query'

        return self._state_0(text)

    def _detect_details(self, text):
        return text.lower().find('details') != -1

    def _detect_previous(self, text):
        return text.lower().find('back') != -1 or text.lower().find('previous') != -1

    def _detect_next(self, text):
        return text.lower().find('next') != -1

    def _detect_start(self, sent):
        flag1, flag2 = sent.lower().find('start'), sent.lower().find('begin')
        return flag1 != -1 or flag2 != -1

    def _extract_verbs(self, sent):
        p = use_udpipe(sent)[0]
        verbs = []
        for word in p:
            if word['upostag'] == 'VERB':
                verbs.append(word['lemma'])

        return verbs

    def _detect_list(self, sent):
        flag = sent.lower().find('list')
        return flag != -1

    def _detect_video(self, sent):
        flag = sent.lower().find('video')
        return flag != -1

    def _detect_exit(self, sent):
        flag = sent.lower().find('exit')
        return flag != -1

    def _detect_more(self, text):
        return text.lower().find('more') != -1 or text.lower().find('next') != -1

    def _show_num(self, sent):
        p = use_udpipe(sent)[0]
        num = -1
        for word in p:
            if word['form'] in num_dict:
                num = num_dict[word['form']]
            elif word['upostag'] == 'NUM':
                num = int(word['form'])
        return num
