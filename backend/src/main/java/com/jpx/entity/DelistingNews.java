package com.jpx.entity;

import jakarta.persistence.*;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;
import java.time.LocalDateTime;

@Entity
@Table(name = "delisting_news")
@Getter
@Setter // 컨트롤러에서 JSON으로 변환하거나 다룰 때 안전하도록 추가
@NoArgsConstructor
public class DelistingNews {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id; // 💡 DB가 int 타입이므로 Integer로 유지하여 에러 방지

    @Column(name = "stock_code") private String stockCode;
    @Column(name = "stock_name") private String stockName;
    @Column(name = "market_type") private String marketType;
    @Column(name = "delisting_date") private String delistingDate;
    @Column(name = "cleanup_start_date") private String cleanupStartDate;
    @Column(name = "cleanup_end_date") private String cleanupEndDate;
    
    @Column(name = "created_at", insertable = false, updatable = false)
    private LocalDateTime createdAt;
}