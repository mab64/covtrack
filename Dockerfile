FROM python:3.7
WORKDIR /var/www/app
COPY . /var/www/app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["flask", "run", "--host=0.0.0.0"]

