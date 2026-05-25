package com.jpx.repository;

import com.jpx.entity.DelistingNews;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface DelistingNewsRepository extends JpaRepository<DelistingNews, Integer> {
    // JpaRepository<엔티티클래스명, PK타입>을 상속받으면 기본적인 CRUD 메서드가 자동으로 생성됩니다.
}