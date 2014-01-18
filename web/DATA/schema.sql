drop table if exists albums;
create table albums(
    Homepage text primary key ,
    Title text,
    Cover text,
    HasPics integer,
    GetPics integer,
    ImgUrls text,
    Times integer DEFAULT 0,
    LogTime date default(datetime('now','localtime'))
);
