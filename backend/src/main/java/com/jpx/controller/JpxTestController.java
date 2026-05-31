package com.jpx.controller;

import com.jpx.entity.DelistingNews;
import com.jpx.repository.DelistingNewsRepository;
import jakarta.servlet.http.HttpServletResponse;
import org.apache.poi.ss.usermodel.*;
import org.apache.poi.xssf.usermodel.XSSFWorkbook;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;
import java.io.IOException;
import java.util.List;

@RestController
public class JpxTestController {
    
    private final DelistingNewsRepository repository;

    public JpxTestController(DelistingNewsRepository repository) {
        this.repository = repository;
    }

    // DB接続テスト用エンドポイント
    @GetMapping("/test-db")
    public List<DelistingNews> testDbConnection() {
        return repository.findAll();
    }

    // 削除銘柄リストをExcel形式でダウンロードするAPI
    @GetMapping("/download-excel")
    public void downloadExcel(HttpServletResponse response) throws IOException {
        // 1. DBから全データを取得
        List<DelistingNews> list = repository.findAll();

        // 2. ワークブック(Excelファイル)の生成
        try (Workbook workbook = new XSSFWorkbook()) {
            // シート名: 上場廃止銘柄一覧
            Sheet sheet = workbook.createSheet("上場廃止銘柄一覧");

            // 3. ヘッダー行の作成
            Row headerRow = sheet.createRow(0);
            String[] headers = {"ID", "銘柄コード", "銘柄名", "市場区分", "上場廃止日", "整理銘柄開始日", "整理銘柄終了日"};
            for (int i = 0; i < headers.length; i++) {
                Cell cell = headerRow.createCell(i);
                cell.setCellValue(headers[i]);
            }

            // 4. DBデータをExcelに書き出し
            int rowNum = 1;
            for (DelistingNews news : list) {
                Row row = sheet.createRow(rowNum++);
                row.createCell(0).setCellValue(news.getId());
                row.createCell(1).setCellValue(news.getStockCode());
                row.createCell(2).setCellValue(news.getStockName());
                row.createCell(3).setCellValue(news.getMarketType());
                row.createCell(4).setCellValue(news.getDelistingDate());
                row.createCell(5).setCellValue(news.getCleanupStartDate());
                row.createCell(6).setCellValue(news.getCleanupEndDate());
            }

            // 5. カラム幅の自動調整
            for (int i = 0; i < headers.length; i++) {
                sheet.autoSizeColumn(i);
                // 自動調整後の幅に少し余裕を持たせる
                sheet.setColumnWidth(i, sheet.getColumnWidth(i) + 512);
            }

            // 6. レスポンスの設定（Excelファイルとしてブラウザに送信）
            response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            response.setHeader("Content-Disposition", "attachment; filename=delisting_list.xlsx");

            // 7. ブラウザへファイル出力
            workbook.write(response.getOutputStream());
        }
    }
}