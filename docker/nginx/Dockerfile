# nginx

FROM nginx:1.21-alpine

# copy files
RUN rm /etc/nginx/conf.d/default.conf
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

ENTRYPOINT nginx -g 'daemon off;'