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

    @GetMapping("/test-db")
    public List<DelistingNews> testDbConnection() {
        return repository.findAll();
    }

    // 💡 엑셀 다운로드 API 추가
    @GetMapping("/download-excel")
    public void downloadExcel(HttpServletResponse response) throws IOException {
        // 1. DB에서 데이터 전부 긁어오기
        List<DelistingNews> list = repository.findAll();

        // 2. 가상의 엑셀 파일(Workbook) 생성
        try (Workbook workbook = new XSSFWorkbook()) {
            Sheet sheet = workbook.createSheet("상장폐지 목록");

            // 3. 헤더 행(첫 번째 줄) 만들기
            Row headerRow = sheet.createRow(0);
            String[] headers = {"ID", "종목코드", "종목명", "시장구분", "상장폐지일", "정리매매 시작일", "정리매매 종료일"};
            for (int i = 0; i < headers.length; i++) {
                Cell cell = headerRow.createCell(i);
                cell.setCellValue(headers[i]);
            }

            // 4. DB 데이터를 한 줄씩 엑셀에 채워넣기
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

            // 💡 여기에 추가: 모든 데이터가 들어간 후 열 너비를 자동으로 맞춤
            for (int i = 0; i < headers.length; i++) {
                sheet.autoSizeColumn(i);
                // 자동 조절된 너비에 256(한 글자 정도)만큼 여유를 더 줌
                sheet.setColumnWidth(i, sheet.getColumnWidth(i) + 512);
            }

            // 5. 브라우저에게 "이 데이터는 엑셀 파일이다"라고 알려주는 설정 (HTTP 헤더)
            response.setContentType("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            response.setHeader("Content-Disposition", "attachment; filename=delisting_news.xlsx");

            // 6. 브라우저로 파일 전송하기
            workbook.write(response.getOutputStream());
        }
    }
}