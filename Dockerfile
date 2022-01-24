FROM public.ecr.aws/lambda/python:3.8
COPY requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN rpm -Uvh https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm
RUN yum -y update
RUN yum -y install tesseract
COPY ./app/app.py   ./
CMD ["app.lambda_handler"]