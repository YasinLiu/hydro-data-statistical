/*
 Navicat Premium Dump SQL

 Source Server         : local-SQLServer
 Source Server Type    : SQL Server
 Source Server Version : 16001000 (16.00.1000)
 Source Host           : 127.0.0.1:1433
 Source Catalog        : CSRRDB
 Source Schema         : dbo

 Target Server Type    : SQL Server
 Target Server Version : 16001000 (16.00.1000)
 File Encoding         : 65001

 Date: 04/02/2026 14:59:16
*/


-- ----------------------------
-- Table structure for Stations
-- ----------------------------
IF EXISTS (SELECT * FROM sys.all_objects WHERE object_id = OBJECT_ID(N'[dbo].[Stations]') AND type IN ('U'))
	DROP TABLE [dbo].[Stations]
GO

CREATE TABLE [dbo].[Stations] (
  [StationID] char(4) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [Cname] char(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [Ctype] char(2) COLLATE Chinese_PRC_CI_AS  NULL,
  [Lognitude] char(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [Latitude] char(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [Xx] numeric(18,2)  NULL,
  [Yy] numeric(18,2)  NULL,
  [Route] char(4) COLLATE Chinese_PRC_CI_AS  NULL,
  [Address] char(40) COLLATE Chinese_PRC_CI_AS  NULL,
  [Lxry] char(8) COLLATE Chinese_PRC_CI_AS  NULL,
  [Zip] char(6) COLLATE Chinese_PRC_CI_AS  NULL,
  [Phone] char(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [LiuYu] char(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [ShuiXi] char(20) COLLATE Chinese_PRC_CI_AS  NULL,
  [HeMing] char(10) COLLATE Chinese_PRC_CI_AS  NULL,
  [Bz] char(80) COLLATE Chinese_PRC_CI_AS  NULL,
  [MapFile] char(100) COLLATE Chinese_PRC_CI_AS  NULL,
  [Lef] numeric(18)  NULL,
  [Topc] numeric(18)  NULL,
  [FzxLb] char(2) COLLATE Chinese_PRC_CI_AS  NULL,
  [SsxsFlag] bit  NULL
)
GO

ALTER TABLE [dbo].[Stations] SET (LOCK_ESCALATION = TABLE)
GO

