from flask import Flask, render_template, request
import re
from parsers import similar_web, plot_similar_web, alexa, website_info
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=['5 per minute', '20 per hour'],
)


# Whitelist localhost
@limiter.request_filter
def ip_whitelist():
    return request.remote_addr == '127.0.0.1'


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        domain = request.form['domain'].lower()
        if re.match(r'^([a-zA-Z0-9-_]+\.)*[a-zA-Z0-9][a-zA-Z0-9-_]+\.[a-zA-Z]{2,11}?$', domain):
            website_data = website_info(domain)
            if 'Error' in website_data.keys():
                return render_template('error.html')
            else:
                alexa_data = alexa(domain)
                similar_web_data = similar_web(domain)
                similar_web_chart = plot_similar_web(similar_web_data)
                return render_template('result.html', alexa_data=alexa_data, website_data=website_data,
                                       domain=domain, similar_web_data=similar_web_data,
                                       similar_web_chart=similar_web_chart)
        else:
            return render_template('query_error.html')
    else:
        return render_template('index.html')


if __name__ == '__main__':
    app.run()
