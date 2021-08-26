FROM python:3.7-alpine
WORKDIR /var/www/app
COPY app .
RUN pip install -r requirements.txt
EXPOSE 5000
ENV FLASK_DEBUG=1
CMD ["flask", "run", "--host=0.0.0.0"]

