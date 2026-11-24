from lumera.crew import extract_reading_profile


def main():
    print("Welcome to Lumera!")

    user_request = input(
        "\nDescreva o livro que voce gostaria de ler: "
    )

    profile = extract_reading_profile(user_request)

    print("\nPerfil de leitura identificado:")
    print(profile.model_dump_json(indent=2))


if __name__ == "__main__":
    main()