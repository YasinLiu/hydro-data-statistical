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

 Date: 04/02/2026 14:59:27
*/


-- ----------------------------
-- Table structure for OneDayData
-- ----------------------------
IF EXISTS (SELECT * FROM sys.all_objects WHERE object_id = OBJECT_ID(N'[dbo].[OneDayData]') AND type IN ('U'))
	DROP TABLE [dbo].[OneDayData]
GO

CREATE TABLE [dbo].[OneDayData] (
  [stationid] char(4) COLLATE Chinese_PRC_CI_AS  NOT NULL,
  [stationindex] char(1) COLLATE Chinese_PRC_CI_AS  NULL,
  [datatime] datetime  NULL,
  [water] numeric(18,2)  NULL,
  [flow] numeric(18,2)  NULL,
  [rain] numeric(18,1)  NULL,
  [voltage] numeric(18,2)  NULL,
  [dataspace] numeric(18)  NULL,
  [status] char(1) COLLATE Chinese_PRC_CI_AS  NULL,
  [rdatatime] datetime  NULL,
  [Flag] bit  NULL,
  [Trantype] char(2) COLLATE Chinese_PRC_CI_AS  NULL,
  [Sourcetype] char(2) COLLATE Chinese_PRC_CI_AS  NULL,
  [Weather] char(1) COLLATE Chinese_PRC_CI_AS  NULL,
  [WaterProof] char(1) COLLATE Chinese_PRC_CI_AS  NULL
)
GO

ALTER TABLE [dbo].[OneDayData] SET (LOCK_ESCALATION = TABLE)
GO

