"""TO-DO: Write a description of what this XBlock is."""

import random

import pkg_resources
from web_fragments.fragment import Fragment
from xblock.core import XBlock
from xblock.fields import Integer, Scope, String, List, Float
from django.http import Http404, HttpResponse, HttpResponseNotFound, StreamingHttpResponse


@XBlock.needs('i18n')
class RatingXBlock(XBlock):
    """
    TO-DO: document what your XBlock does.
    """

    # Fields are defined on the class.  You can access them in your code as
    # self.<fieldname>.

    prompts = List(
        default=[
            {'freeform': "Nhận xét",
             'likert': "Chọn để đánh giá khoá học"}
        ],
        scope=Scope.settings,
        help="Freeform user prompt",
        xml_node=True
    )

    prompt_choice = Integer(
        default=-1, scope=Scope.user_state,
        help="Random number generated for p. -1 if uninitialized"
    )

    user_vote = Integer(
        default=-1, scope=Scope.user_state,
        help="How user voted. -1 if didn't vote"
    )
    user_review = Integer(
        default=-1, scope=Scope.user_state,
        help="How user review. -1 if didn't review"
    )

    p = Float(
        default=100, scope=Scope.settings,
        help="What percent of the time should this show?"
    )

    p_user = Float(
        default=-1, scope=Scope.user_state,
        help="Random number generated for p. -1 if uninitialized"
    )

    vote_aggregate = List(
        default=None, scope=Scope.user_state_summary,
        help="A list of user votes"
    )

    user_freeform = String(default="", scope=Scope.user_state,
                           help="Feedback")

    display_name = String(
        display_name="Display Name",
        default="Đánh giá khoá học",
        scopde=Scope.settings
    )

    total_reviews = Integer(
        default=0, scope=Scope.user_state_summary,
        help="total user review. 0 if didn't review"
    )

    total_votes = Integer(
        default=0, scope=Scope.user_state_summary,
        help="total user vote. 0 if didn't vote"
    )

    avg_rating = Float(default=0, scope=Scope.user_state_summary)

    total = Float(default=0, scope=Scope.user_state_summary)

    def resource_string(self, path):
        """Handy helper for getting resources from our kit."""
        data = pkg_resources.resource_string(__name__, path)
        return data.decode("utf8")

    
    def get_prompt(self, index=-1):
        """
        Return the current prompt dictionary, doing appropriate
        randomization if necessary, and falling back to defaults when
        necessary.
        """
        if index == -1:
            index = self.prompt_choice

        _ = self.runtime.service(self, 'i18n').ugettext
        prompt = {
            'freeform': _("Nhận xét"),
            'likert': _("Chọn để đánh giá khoá học"),
            'mouseovers': [_("Poor"),
                           _("Fair"),
                           _("Average"),
                           _("Good"),
                           _("Excellent")],
            'icons': ["😭", "😞","😐", "😊", "😁"]
        }

        prompt.update(self.prompts[index])
        return prompt

    def student_view(self, context=None):
        """
        The primary view of the RateXBlock, shown to students
        when viewing courses.
        """
        # Figure out which prompt we show. We set self.prompt_choice to
        # the index of the prompt. We set it if it is out of range (either
        # uninitiailized, or incorrect due to changing list length). Then,
        # we grab the prompt, prepopulated with defaults.
        if self.prompt_choice < 0 or self.prompt_choice >= len(self.prompts):
            self.prompt_choice = random.randint(0, len(self.prompts) - 1)
        prompt = self.get_prompt()

        # Now, we render the RateXBlock. This may be redundant, since we
        # don't always show it.
        html = self.resource_string("static/html/rate.html")
        # The replace allows us to format the HTML nicely without getting
        # extra whitespace
        scale_item = self.resource_string("static/html/scale_item.html")
        scale_item = scale_item.replace('\n', '')
        indexes = list(range(5))
        active_vote = ["checked" if i == self.user_vote else ""
                       for i in indexes]

        self.init_vote_aggregate()
        # init avg, total vote, total review, vote arr
        
        votes = self.vote_aggregate
        scale = "".join(
            scale_item.format(i=i, active=a, votes=v) for
            (i, a, v) in
            zip(indexes, active_vote, votes)
        )
        scale = "<div class='star'>" + scale + "</div>"
        if self.user_vote != -1:
            _ = self.runtime.service(self, 'i18n').ugettext
            response = _("Bạn đã đánh giá khoá học!")
        else:
            response = "Vui lòng đánh giá khoá học!"
        rendered = html.format(self=self,
                               scale=scale,
                               freeform_prompt=prompt['freeform'],
                               likert_prompt=prompt['likert'],
                               total_reviews=self.total_reviews,
                               response=response)

        # We initialize self.p_user if not initialized -- this sets whether
        # or not we show it. From there, if it is less than odds of showing,
        # we set the fragment to the rendered XBlock. Otherwise, we return
        # empty HTML. There ought to be a way to return None, but XBlocks
        # doesn't support that.
        if self.p_user == -1:
            self.p_user = random.uniform(0, 100)
        if self.p_user < self.p:
            frag = Fragment(rendered)
        else:
            frag = Fragment("")

        # Finally, we do the standard JS+CSS boilerplate. Honestly, XBlocks
        # ought to have a sane default here.
        frag.add_css(self.resource_string("static/css/ratingxblock.css"))
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css")
        frag.add_javascript(self.resource_string("static/js/src/rate.js"))
        frag.initialize_js('RatingXBlock')
        return frag

    def show_feedback(self, context=None):

        if self.prompt_choice < 0 or self.prompt_choice >= len(self.prompts):
            self.prompt_choice = random.randint(0, len(self.prompts) - 1)
        prompt = self.get_prompt()

        html = self.resource_string("static/html/show_feedback.html")

        scale_item = self.resource_string("static/html/scale_item.html")
        scale_item = scale_item.replace('\n', '')
        indexes = list(range(len(prompt['icons'])))
        active_vote = ["checked" if i == self.user_vote else ""
                       for i in indexes]
        self.init_vote_aggregate()
        votes = self.vote_aggregate
        scale = "".join(
            scale_item.format(level=l, icon=icon, i=i, active=a, votes=v) for
            (l, icon, i, a, v) in
            zip(prompt['mouseovers'], prompt['icons'], indexes, active_vote, votes)
        )
        scale = "<div> AVG RATING: "+ str(self.avg_rating) +"</div>"+ "<div> TOTAL REVIEW: "+ str(self.total_reviews) +"</div>" + "<div class='star'>" + scale + "</div>"

        total_view_html = self.resource_string("static/html/ratingxblock.html")

        rendered = html.format(self=self,
                               scale=scale,
                               total_view_html=total_view_html)


        if self.p_user == -1:
            self.p_user = random.uniform(0, 100)
        if self.p_user < self.p:
            frag = Fragment(rendered)
        else:
            frag = Fragment("")

        # Finally, we do the standard JS+CSS boilerplate. Honestly, XBlocks
        frag.add_css(self.resource_string("static/css/ratingxblock.css"))
        frag.add_css_url("https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css")
        frag.add_javascript(self.resource_string("static/js/src/rate.js"))
        frag.initialize_js('RatingXBlock')
        return frag

    # TO-DO: change this to create the scenarios you'd like to see in the
    # workbench while developing your XBlock.
    @staticmethod
    def workbench_scenarios():
        """A canned scenario for display in the workbench."""
        return [
            ("RatingXBlock",
             """<ratingxblock/>
             """),
            ("Multiple RatingXBlock",
             """<vertical_demo>
                <ratingxblock/>
                <ratingxblock/>
                <ratingxblock/>
                </vertical_demo>
             """),
        ]

    def init_vote_aggregate(self):
        # Make sure we're initialized
        if not self.vote_aggregate:
            self.vote_aggregate = [0] * (len(self.get_prompt()['mouseovers']))

    def vote(self, data):
        """
        Handle voting
        """
        # prompt_choice is initialized by student view.
        # Ideally, we'd break this out into a function.
        if self.user_vote == data['vote']:
            return

        prompt = self.get_prompt(self.prompt_choice)
        # Make sure we're initialized
        self.init_vote_aggregate()

        # Remove old vote if we voted before
        if self.user_vote != -1:
            self.vote_aggregate[self.user_vote] -= 1
            self.total = self.total - self.user_vote + data['vote']
        else:
            self.total = self.total + data['vote'] + 1
        if data['vote'] != -1 and self.user_vote == -1:
            self.avg_rating = (self.avg_rating * self.total_votes + (data['vote'] + 1)) / (self.total_votes + 1)
            self.total_votes += 1
        else:
            self.avg_rating = (self.avg_rating * self.total_votes - (self.user_vote + 1) + (data['vote'] + 1)) / self.total_votes
        
        self.user_vote = data['vote']
        self.vote_aggregate[data['vote']] += 1
    
    def is_staff(self):
        """
        Return self.xmodule_runtime.user_is_staff if available

        This is not a supported part of the XBlocks API in all
        runtimes, and this is a workaround so something reasonable
        happens in both workbench and edx-platform
        """
        if hasattr(self, "xmodule_runtime") and \
           hasattr(self.xmodule_runtime, "user_is_staff"):
            return self.xmodule_runtime.user_is_staff
        else:
            # In workbench and similar settings, always return true
            return True

    @XBlock.json_handler
    def feedback(self, data, suffix=''):
        '''
        Allow students to submit feedback, both numerical and
        qualitative. We only update the specific type of feedback
        submitted.

        We return the current state. While this is not used by the
        client code, it is helpful for testing. For staff users, we
        also return the aggregate results.
        '''
        _ = self.runtime.service(self, 'i18n').ugettext

        if 'vote' not in data or data['vote'] == -1:
            response = {"success": True,
                        "response": _("Bạn chưa đánh giá khoá học!")}
            self.runtime.publish(self,
                                 'edx.ratexblock.nothing_provided',
                                 {})
            return response
        if 'freeform' in data:
            response = {"success": True,
                        "response": _("Đánh giá khoá học thành công!")}
            self.runtime.publish(self,
                                 'edx.ratexblock.freeform_provided',
                                 {'old_freeform': self.user_freeform,
                                 'new_freeform': data['freeform']})
            if self.user_freeform != '' and data['freeform'] == '':
                self.total_reviews -= 1
            elif self.user_freeform == '' and data['freeform'] != '':
                self.total_reviews += 1
            self.user_freeform = data['freeform']
            
        if 'vote' in data:
            response = {"success": True,
                        "response": _("Đánh giá khoá học thành công!")}
            self.runtime.publish(self,
                         'edx.ratexblock.likert_provided',
                         {'old_vote': self.user_vote,
                          'new_vote': data['vote']})
            self.vote(data)

        response.update({
            "freeform": self.user_freeform,
            "vote": self.user_vote
        })

        response['aggregate'] = self.vote_aggregate
        # response['flag'] = self.student_view()

        return response



    