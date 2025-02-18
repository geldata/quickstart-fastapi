CREATE MIGRATION m1fdtcahp3bnur3a7ujccvw3rclyjyr4q4jyp4w2hllrkrujgfhvma
    ONTO initial
{
  CREATE TYPE default::Card {
      CREATE REQUIRED PROPERTY back: std::str;
      CREATE REQUIRED PROPERTY front: std::str;
      CREATE REQUIRED PROPERTY order: std::int64;
  };
  CREATE TYPE default::Deck {
      CREATE MULTI LINK cards: default::Card {
          ON TARGET DELETE ALLOW;
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE PROPERTY description: std::str;
      CREATE REQUIRED PROPERTY name: std::str;
  };
};
