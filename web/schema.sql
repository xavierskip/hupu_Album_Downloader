CREATE DATABASE hupu DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;

USE hupu;

CREATE TABLE `albums` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) NOT NULL,
  `title` varchar(255) NOT NULL,
  `cover` mediumtext NOT NULL,
  `pics` int(11) NOT NULL,
  `getPics` int(11) NOT NULL,
  `picsUrls` mediumtext NOT NULL,
  `times` int(11) NOT NULL DEFAULT '1',
  `logTime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`)
) ENGINE=InnoDB AUTO_INCREMENT=0 DEFAULT CHARSET=utf8;

CREATE TABLE `users` (
  `uid` bigint(20) unsigned NOT NULL,
  `access_token` varchar(255) NOT NULL,
  `avatar` varchar(255) NOT NULL,
  `name` varchar(32) NOT NULL DEFAULT '',
  `province` int(11) NOT NULL,
  `city` int(11) NOT NULL,
  `location` varchar(255) NOT NULL,
  `description` varchar(255) NOT NULL,
  `blog` varchar(255) NOT NULL,
  `gender` varchar(1) NOT NULL DEFAULT '',
  `followers` int(11) NOT NULL,
  `friends` int(11) NOT NULL,
  `statuses` int(11) NOT NULL,
  `created` varchar(255) NOT NULL,
  `avatar_hd` varchar(255) NOT NULL,
  PRIMARY KEY (`uid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;