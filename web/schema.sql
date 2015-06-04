CREATE DATABASE hupu DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

USE hupu;

CREATE TABLE `albums` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(128) NOT NULL DEFAULT '',
  `title` varchar(32) NOT NULL DEFAULT '',
  `cover` text NOT NULL,
  `pics` int(11) NOT NULL,
  `getPics` int(11) NOT NULL,
  `picsUrls` text NOT NULL,
  `times` int(11) NOT NULL DEFAULT '1',
  `logTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;

CREATE TABLE `users` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `uid` int(11) NOT NULL,
  `name` varchar(11) NOT NULL DEFAULT '',
  `avatar` varchar(128) NOT NULL DEFAULT '',
  `access_token` varchar(11) NOT NULL DEFAULT '',
  `province` int(11) NOT NULL,
  `city` int(11) NOT NULL,
  `location` varchar(11) NOT NULL DEFAULT '',
  `description` varchar(128) NOT NULL DEFAULT '',
  `blog` varchar(128) NOT NULL DEFAULT '',
  `gender` char(11) NOT NULL DEFAULT '',
  `followers` int(11) NOT NULL,
  `friends` int(11) NOT NULL,
  `statuses` int(11) NOT NULL,
  `created` varchar(32) NOT NULL DEFAULT '',
  `avatar_hd` varchar(128) NOT NULL DEFAULT '',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;