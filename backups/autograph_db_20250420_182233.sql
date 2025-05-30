PGDMP     !                    }           autograph_db    14.17 (Homebrew)    14.17 (Homebrew)     p           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            q           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            r           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            s           1262    17431    autograph_db    DATABASE     W   CREATE DATABASE autograph_db WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE = 'C';
    DROP DATABASE autograph_db;
                hassan    false            t           0    0    DATABASE autograph_db    ACL     v   GRANT CONNECT ON DATABASE autograph_db TO autograph_app_role;
GRANT CONNECT ON DATABASE autograph_db TO autograph_db;
                   hassan    false    3699            u           0    0    autograph_db    DATABASE PROPERTIES     >   ALTER DATABASE autograph_db SET statement_timeout TO '30000';
                     hassan    false            v           0    0    SCHEMA public    ACL     b   GRANT USAGE ON SCHEMA public TO autograph_app_role;
GRANT USAGE ON SCHEMA public TO autograph_db;
                   hassan    false    3            �            1259    17938    alembic_version    TABLE     X   CREATE TABLE public.alembic_version (
    version_num character varying(32) NOT NULL
);
 #   DROP TABLE public.alembic_version;
       public         heap    hassan    false            w           0    0    TABLE alembic_version    ACL     ;   GRANT ALL ON TABLE public.alembic_version TO autograph_db;
          public          hassan    false    209            �            1259    25694 
   autographs    TABLE     �   CREATE TABLE public.autographs (
    id integer NOT NULL,
    instagram_url character varying(255) NOT NULL,
    encryption_code text NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);
    DROP TABLE public.autographs;
       public         heap    hassan    false            �            1259    25693    autographs_id_seq    SEQUENCE     �   CREATE SEQUENCE public.autographs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.autographs_id_seq;
       public          hassan    false    211            x           0    0    autographs_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.autographs_id_seq OWNED BY public.autographs.id;
          public          hassan    false    210            �            1259    25704    invite_codes    TABLE     (  CREATE TABLE public.invite_codes (
    id integer NOT NULL,
    code character varying(32) NOT NULL,
    instagram_handle character varying(80) NOT NULL,
    is_used boolean DEFAULT false,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    used_at timestamp with time zone
);
     DROP TABLE public.invite_codes;
       public         heap    hassan    false            �            1259    25703    invite_codes_id_seq    SEQUENCE     �   CREATE SEQUENCE public.invite_codes_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.invite_codes_id_seq;
       public          hassan    false    213            y           0    0    invite_codes_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.invite_codes_id_seq OWNED BY public.invite_codes.id;
          public          hassan    false    212            �           2604    25697    autographs id    DEFAULT     n   ALTER TABLE ONLY public.autographs ALTER COLUMN id SET DEFAULT nextval('public.autographs_id_seq'::regclass);
 <   ALTER TABLE public.autographs ALTER COLUMN id DROP DEFAULT;
       public          hassan    false    210    211    211            �           2604    25707    invite_codes id    DEFAULT     r   ALTER TABLE ONLY public.invite_codes ALTER COLUMN id SET DEFAULT nextval('public.invite_codes_id_seq'::regclass);
 >   ALTER TABLE public.invite_codes ALTER COLUMN id DROP DEFAULT;
       public          hassan    false    212    213    213            i          0    17938    alembic_version 
   TABLE DATA           6   COPY public.alembic_version (version_num) FROM stdin;
    public          hassan    false    209   G       k          0    25694 
   autographs 
   TABLE DATA           T   COPY public.autographs (id, instagram_url, encryption_code, created_at) FROM stdin;
    public          hassan    false    211   q       m          0    25704    invite_codes 
   TABLE DATA           `   COPY public.invite_codes (id, code, instagram_handle, is_used, created_at, used_at) FROM stdin;
    public          hassan    false    213          z           0    0    autographs_id_seq    SEQUENCE SET     @   SELECT pg_catalog.setval('public.autographs_id_seq', 38, true);
          public          hassan    false    210            {           0    0    invite_codes_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.invite_codes_id_seq', 16, true);
          public          hassan    false    212            �           2606    17942 #   alembic_version alembic_version_pkc 
   CONSTRAINT     j   ALTER TABLE ONLY public.alembic_version
    ADD CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num);
 M   ALTER TABLE ONLY public.alembic_version DROP CONSTRAINT alembic_version_pkc;
       public            hassan    false    209            �           2606    25702    autographs autographs_pkey 
   CONSTRAINT     X   ALTER TABLE ONLY public.autographs
    ADD CONSTRAINT autographs_pkey PRIMARY KEY (id);
 D   ALTER TABLE ONLY public.autographs DROP CONSTRAINT autographs_pkey;
       public            hassan    false    211            �           2606    25713 "   invite_codes invite_codes_code_key 
   CONSTRAINT     ]   ALTER TABLE ONLY public.invite_codes
    ADD CONSTRAINT invite_codes_code_key UNIQUE (code);
 L   ALTER TABLE ONLY public.invite_codes DROP CONSTRAINT invite_codes_code_key;
       public            hassan    false    213            �           2606    25711    invite_codes invite_codes_pkey 
   CONSTRAINT     \   ALTER TABLE ONLY public.invite_codes
    ADD CONSTRAINT invite_codes_pkey PRIMARY KEY (id);
 H   ALTER TABLE ONLY public.invite_codes DROP CONSTRAINT invite_codes_pkey;
       public            hassan    false    213            i      x�3H5M�0J37��0����� *9�      k   �  x����N�@�5<�+7���ܙNgbh�BQ�`mLbi+����<�
+��	�Op��s/5Z�z�J�ʲDQZ���j��Y�h��3��2�, �b�N&E�Y��NLJ�m2��I���((��w=3>_�^��i]_�Y<�zv�b��1;���p����g���ldX��A6w��0>H�w��0���L1@�� h`�|?�zV"�ra�߻�H��|Ḧ�IMLq�t)15v�ϒn*>���z��K��Q���w�<��T4u����h�/���{XNG�@&���}��Wu>7ٕ������X
��kN3���I�?K���Y��H�"��0cD���Mg��a���<����1(V�"�s��xE�v��Q�      m   �   x�e�=
�@��z���efv�� ��n)�,Q$"��ۛ-��;����8B����ȶB�7dJb�������\M��E��bh��=��W8��cbҞ8�<�eeaCnc�'�$"��?�h1��p�a(�WJYI�x�M����+;��z$�2�     